import ast
import hashlib
import json
import re
import stat
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit
from .source import python_details, manifest_details, resolve_imports
from .binary import identify, inspect_binary
from .platform import CONFIG_NAMES, config_details, platform_profile
from .explain import explain_software
from .tracing import trace_routes
from .feature_map import build_feature_map
from .js_tracing import trace_javascript

LANGUAGES = {'.py': 'Python', '.js': 'JavaScript', '.jsx': 'JavaScript', '.ts': 'TypeScript', '.tsx': 'TypeScript', '.java': 'Java', '.cs': 'C#', '.php': 'PHP', '.go': 'Go', '.rs': 'Rust', '.c': 'C', '.cpp': 'C++', '.h': 'C/C++'}
BINARY = {'.exe', '.dll', '.apk', '.so', '.class', '.jar', '.dylib'}
MANIFESTS = {'package.json', 'requirements.txt', 'pyproject.toml', 'pom.xml', 'Cargo.toml', 'go.mod', 'composer.json'}
MAX_FILES = 10000
MAX_TOTAL = 256 * 1024 * 1024
MAX_FILE = 4 * 1024 * 1024


def inspect_zip(path):
    """Read bounded archive members in memory. Never extract or execute inputs."""
    report = {'schema_version': 3, 'files': [], 'findings': [], 'warnings': [], 'scope': 'Static ZIP inspection; no input code is executed.'}
    python_trees = {}
    js_sources = {}
    js_source_bytes = 0
    trace_source_bytes = 0
    def finding(kind, value, file, line, confidence='observed'):
        report['findings'].append({'kind': kind, 'value': str(value)[:300], 'confidence': confidence, 'evidence': {'file': file, 'line': line}})
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if len(members) > MAX_FILES:
            raise ValueError('Archive exceeds 10,000 entries.')
        if sum(m.file_size for m in members) > MAX_TOTAL:
            raise ValueError('Archive exceeds 256 MiB uncompressed.')
        seen = set()
        for member in members:
            name = member.filename.replace('\\', '/')
            p = PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts or ':' in name or '\x00' in name or stat.S_ISLNK(member.external_attr >> 16):
                raise ValueError('Unsafe archive member path or symbolic link.')
            name = p.as_posix()
            if name in seen:
                raise ValueError('Duplicate archive member path.')
            seen.add(name)
            if member.is_dir():
                continue
            suffix = p.suffix.lower()
            item = {'path': name, 'bytes': member.file_size, 'language': LANGUAGES.get(suffix), 'category': 'binary' if suffix in BINARY else 'source' if suffix in LANGUAGES else 'other'}
            item['analysis'] = 'inventory_only'
            report['files'].append(item)
            if member.flag_bits & 1:
                report['warnings'].append(f'{name}: encrypted; content skipped.')
                continue
            if member.file_size > MAX_FILE or member.file_size / max(member.compress_size, 1) > 200:
                report['warnings'].append(f'{name}: content skipped by size/compression limit.')
                continue
            with archive.open(member) as stream:
                prefix = stream.read(4096)
                detected = identify(prefix)
                if not detected and suffix not in BINARY and suffix not in LANGUAGES and p.name not in MANIFESTS | CONFIG_NAMES:
                    continue
                data = prefix + stream.read(MAX_FILE + 1 - len(prefix))
            if len(data) > MAX_FILE:
                raise ValueError('Member exceeds read limit.')
            item['sha256'] = hashlib.sha256(data).hexdigest()
            binary = inspect_binary(data, name, suffix in BINARY)
            if binary:
                metadata, binary_findings = binary
                item.update(category='binary', language=None, analysis='binary_static', binary=metadata)
                report['findings'].extend(binary_findings)
                report['warnings'].extend(f'{name}: {note}' for note in metadata['notes'])
                continue
            try:
                source = data.decode('utf-8-sig')
            except UnicodeDecodeError:
                report['warnings'].append(f'{name}: unsupported text encoding.')
                continue
            item['lines'] = len(source.splitlines())
            if p.name in CONFIG_NAMES:
                item['analysis'] = 'config_heuristic'
                config_details(source, name, finding)
                continue
            item['analysis'] = 'heuristic' if suffix in {'.js', '.jsx', '.ts', '.tsx'} else 'manifest' if p.name in MANIFESTS else 'inventory_only'
            if suffix in {'.js', '.ts'}:
                if len(js_sources) < 128 and js_source_bytes + len(data) <= 16 * 1024 * 1024:
                    js_sources[name] = source
                    js_source_bytes += len(data)
                else:
                    report['warnings'].append(f'{name}: JS/TS helper tracing input cap reached (128 files / 16 MiB).')
            if p.name in MANIFESTS:
                finding('manifest', p.name, name, 1)
                manifest_details(source, name, finding)
            if p.name == 'package.json':
                try:
                    manifest = json.loads(source)
                    for section in ('dependencies', 'devDependencies', 'peerDependencies'):
                        deps = manifest.get(section, {}) if isinstance(manifest, dict) else {}
                        if isinstance(deps, dict):
                            for dependency in deps:
                                line = next((i for i, text in enumerate(source.splitlines(), 1) if json.dumps(dependency) in text), 1)
                                finding('dependency', dependency, name, line)
                except (ValueError, TypeError):
                    report['warnings'].append(f'{name}: invalid package manifest.')
            if suffix == '.py':
                try:
                    tree = ast.parse(source)
                    if len(python_trees) < 128 and trace_source_bytes + len(data) <= 16 * 1024 * 1024:
                        python_trees[name] = tree
                        trace_source_bytes += len(data)
                    else:
                        message = 'Python helper tracing input capped at 128 files / 16 MiB source; other AST findings remain available.'
                        if message not in report['warnings']:
                            report['warnings'].append(message)
                    item['analysis'] = 'python_ast'
                    python_details(tree, name, finding)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                finding('import', alias.name, name, node.lineno)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                finding('import', '.' * node.level + node.module, name, node.lineno)
                        elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                            finding('symbol', node.name, name, node.lineno)
                        elif isinstance(node, ast.If) and isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__' and any(isinstance(c, ast.Constant) and c.value == '__main__' for c in node.test.comparators):
                            finding('entry_point', '__main__ guard', name, node.lineno)
                except (SyntaxError, RecursionError):
                    item['analysis'] = 'parse_failed'
                    report['warnings'].append(f'{name}: Python parse failed; heuristic scanning only.')
            for number, line in enumerate(source.splitlines(), 1):
                if suffix in {'.js', '.jsx', '.ts', '.tsx'}:
                    for match in re.finditer(r'''(?:\bfrom\s*|\brequire\s*\(\s*|\bimport\s*)['"]([^'"\n]+)['"]''', line):
                        finding('import', match.group(1), name, number, 'heuristic')
                route = re.search(r'''(?:@\w+\.(?:route|get|post|put|delete|patch)|\b\w+\.(?:get|post|put|delete|patch))\s*\(\s*['"]([^'"\n]+)''', line)
                if route and suffix != '.py':
                    finding('route_candidate', route.group(1), name, number, 'heuristic')
                for match in re.finditer(r'''https?://[^\s'"<>]+''', line):
                    try:
                        parsed = urlsplit(match.group(0))
                        if parsed.hostname:
                            finding('endpoint_host_candidate', parsed.scheme + '://' + parsed.hostname, name, number, 'heuristic')
                    except ValueError:
                        continue
    resolve_imports(report)
    trace_routes(report, python_trees)
    trace_javascript(report, js_sources)
    report['summary'] = {'files': len(report['files']), 'bytes': sum(f['bytes'] for f in report['files']), 'languages': dict(Counter(f['language'] for f in report['files'] if f['language'])), 'binary_candidates': sum(f['category'] == 'binary' for f in report['files']), 'findings': len(report['findings'])}
    report['coverage'] = dict(Counter(f['analysis'] for f in report['files']))
    report['platform'] = platform_profile(report)
    report['behavior'] = explain_software(report)
    report['feature_map'] = build_feature_map(report)
    report['limitations'] = ['Python symbols/imports use AST parsing; JavaScript/TypeScript imports and endpoint-host candidates use heuristics.', 'Other source languages are inventoried only. No complete call graph, runtime behavior, vulnerability audit, or business requirements recovery is claimed.', 'Binary inspection is bounded static metadata analysis, not decompilation or behavioral verification. Mach-O and DEX receive header identification only. Malformed binaries retain partial findings.', 'Nested containers receive directory inspection only. Files over 4 MiB or compression limits are inventoried without content inspection. Binary string samples may contain private content; URL hosts omit credentials, paths and queries.']
    report['limitations'] += ['Local module links are path candidates, not runtime resolution. Aliases, custom search paths, re-exports and dynamic imports may remain unresolved. Ambiguous matches are not selected.', 'Python decorator routes and ORM base-class names are syntax candidates, not verified framework behavior. Non-Python route and import scans can match comments.', 'Only package.json, requirements.txt and go.mod dependencies are extracted. Other known manifests are identified only. File changes are compared only when both reports contain inspected-content hashes.']
    report['limitations'].append('Python AST traces cover module-level handlers/helpers, simple SQLite statements and selected requests/httpx host references. JS/TS uses a conservative token recognizer for selected ES-module Express callbacks/helpers and pg/mysql2 literal SQL, not a full parser. CommonJS, JSX/TSX, ORM, class-based, dynamic and complex middleware behavior are untraced. Bounds: 128 files / 16 MiB per source family, 100 combined routes, helper depth 3 / 12 functions and 40 operations per trace; Python scans 10,000 nodes per function and JS/TS 60,000 tokens per file. Branch outcomes and successful execution remain unverified.')
    return report
