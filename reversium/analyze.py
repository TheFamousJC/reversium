import ast
import hashlib
import json
import re
import stat
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit
from .handover import setup_details, build_handover, TEMPLATES
from .source import python_details, manifest_details, resolve_imports
from .binary import identify, inspect_binary
from .platform import CONFIG_NAMES, config_details, platform_profile
from .explain import explain_software
from .tracing import trace_routes
from .feature_map import build_feature_map
from .js_tracing import trace_javascript
from .workspace_tracing import trace_workspace

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
    sql_sources = {}
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
                if not detected and suffix not in BINARY and suffix not in LANGUAGES and suffix != '.sql' and p.name not in MANIFESTS | CONFIG_NAMES | TEMPLATES:
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
            setup_details(source, name, finding)
            item['lines'] = len(source.splitlines())
            if suffix == '.sql':
                if len(sql_sources) < 128 and sum(len(s) for s in sql_sources.values()) + len(source) <= 16 * 1024 * 1024:
                    sql_sources[name] = source
                    item['analysis'] = 'sql_reference_scan'
                else:
                    report['warnings'].append(f'{name}: SQL reference input limit reached.')
                continue
            if p.name in CONFIG_NAMES:
                item['analysis'] = 'config_heuristic'
                config_details(source, name, finding)
                continue
            item['analysis'] = 'heuristic' if suffix in {'.js', '.jsx', '.ts', '.tsx'} else 'manifest' if p.name in MANIFESTS else 'inventory_only'
            if suffix in {'.js', '.ts', '.tsx', '.jsx'}:
                if len(js_sources) < 256 and js_source_bytes + len(data) <= 16 * 1024 * 1024:
                    js_sources[name] = source
                    js_source_bytes += len(data)
                else:
                    report['warnings'].append(f'{name}: JS/TS helper tracing input cap reached (256 files / 16 MiB).')
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
    trace_javascript(report, {f: s for f, s in js_sources.items() if not f.endswith(('.tsx', '.jsx'))})
    trace_workspace(report, js_sources, sql_sources)
    report['summary'] = {'files': len(report['files']), 'bytes': sum(f['bytes'] for f in report['files']), 'languages': dict(Counter(f['language'] for f in report['files'] if f['language'])), 'binary_candidates': sum(f['category'] == 'binary' for f in report['files']), 'findings': len(report['findings'])}
    report['coverage'] = dict(Counter(f['analysis'] for f in report['files']))
    report['platform'] = platform_profile(report)
    report['feature_map'] = build_feature_map(report)
    report['behavior'] = explain_software(report)
    report['limitations'] = ['Python symbols/imports use AST parsing; JavaScript/TypeScript imports and endpoint-host candidates use heuristics.', 'Source languages beyond the supported Python, JS/TS and SQL reference readers are inventoried only. No complete call graph, runtime behavior, vulnerability audit, or business requirements recovery is claimed.', 'Binary inspection is bounded static metadata analysis, not decompilation or behavioral verification. Mach-O and DEX receive header identification only. Malformed binaries retain partial findings.', 'Nested containers receive directory inspection only. Files over 4 MiB or compression limits are inventoried without content inspection. Binary string samples may contain private content; URL hosts omit credentials, paths and queries.']
    report['limitations'] += ['Local module links are path candidates, not runtime resolution. Aliases, custom search paths, re-exports and dynamic imports may remain unresolved. Ambiguous matches are not selected.', 'Python decorator routes and ORM base-class names are syntax candidates, not verified framework behavior. Non-Python route and import scans can match comments.', 'Only package.json, requirements.txt and go.mod dependencies are extracted. Other known manifests are identified only. File changes are compared only when both reports contain inspected-content hashes.']
    report['limitations'].append('Python AST traces and selected pg/mysql2 operation traces retain their bounded execution-path approximation. The additional TS/React/Supabase graph records lexical references, including conditional code and callbacks, not proven execution. Regex and JSX text are opaque; JSX expressions/component references are scanned. Supabase clients are recognized through named imports, factories, aliases and annotated parameters; dynamic receivers, object-property clients, re-exports, namespace imports, complex prop/event data flow and runtime middleware effects remain unknown. Selected explicit JSX prop bindings, destructured/object props, immutable callback aliases, React useCallback/returned-hook callbacks and literal React.lazy imports receive candidate links. Multiple component usages are combined as possible bindings, not runtime instances. Computed fetch targets use bounded constant strings/concatenation/templates and per-caller helper arguments with method-aware route candidates; arbitrary expressions, mutable bindings, unknown origins and methods remain unresolved. Literal router mounts and API-path matches are candidates, not verified routing. SQL RPC/table links are migration-name candidates; dynamic SQL, applied migrations, RLS and database identity are unverified. Bounds: JS/TS 256 files / 16 MiB, SQL 128 files / 16 MiB, 60,000 tokens per JS file; workspace 4,000 nodes / 12,000 edges; feature traversal depth 10 / 360 nodes; computed API helper depth 4 / 5,000 contexts / 400 outputs, 2,000 characters per target expression. Graph display caps 120 nodes / 240 edges per selected view. Python retains 128 files, 100 routes and depth 3 / 12 functions per trace. No source is evaluated.')
    report['handover'] = build_handover(report)
    return report
