import ast
import hashlib
import json
import re
import stat
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

LANGUAGES = {'.py': 'Python', '.js': 'JavaScript', '.jsx': 'JavaScript', '.ts': 'TypeScript', '.tsx': 'TypeScript', '.java': 'Java', '.cs': 'C#', '.php': 'PHP', '.go': 'Go', '.rs': 'Rust', '.c': 'C', '.cpp': 'C++', '.h': 'C/C++'}
BINARY = {'.exe', '.dll', '.apk', '.so', '.class', '.jar', '.dylib'}
MANIFESTS = {'package.json', 'requirements.txt', 'pyproject.toml', 'pom.xml', 'Cargo.toml', 'go.mod', 'composer.json'}
MAX_FILES = 10000
MAX_TOTAL = 256 * 1024 * 1024
MAX_FILE = 4 * 1024 * 1024


def inspect_zip(path):
    """Read bounded archive members in memory. Never extract or execute inputs."""
    report = {'schema_version': 1, 'files': [], 'findings': [], 'warnings': [], 'scope': 'Static ZIP inspection; no input code is executed.'}
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
            if name in seen:
                raise ValueError('Duplicate archive member path.')
            seen.add(name)
            if member.is_dir():
                continue
            suffix = p.suffix.lower()
            item = {'path': name, 'bytes': member.file_size, 'language': LANGUAGES.get(suffix), 'category': 'binary' if suffix in BINARY else 'source' if suffix in LANGUAGES else 'other'}
            report['files'].append(item)
            if member.flag_bits & 1:
                report['warnings'].append(f'{name}: encrypted; content skipped.')
                continue
            if member.file_size > MAX_FILE or member.file_size / max(member.compress_size, 1) > 200:
                report['warnings'].append(f'{name}: content skipped by size/compression limit.')
                continue
            if suffix not in LANGUAGES and p.name not in MANIFESTS:
                continue
            with archive.open(member) as stream:
                data = stream.read(MAX_FILE + 1)
            if len(data) > MAX_FILE:
                raise ValueError('Member exceeds read limit.')
            item['sha256'] = hashlib.sha256(data).hexdigest()
            try:
                source = data.decode('utf-8-sig')
            except UnicodeDecodeError:
                report['warnings'].append(f'{name}: unsupported text encoding.')
                continue
            item['lines'] = len(source.splitlines())
            if p.name in MANIFESTS:
                finding('manifest', p.name, name, 1)
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
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                finding('import', alias.name, name, node.lineno)
                        elif isinstance(node, ast.ImportFrom):
                            finding('import', '.' * node.level + (node.module or ''), name, node.lineno)
                        elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                            finding('symbol', node.name, name, node.lineno)
                        elif isinstance(node, ast.If) and isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__' and any(isinstance(c, ast.Constant) and c.value == '__main__' for c in node.test.comparators):
                            finding('entry_point', '__main__ guard', name, node.lineno)
                except (SyntaxError, RecursionError):
                    report['warnings'].append(f'{name}: Python parse failed; heuristic scanning only.')
            for number, line in enumerate(source.splitlines(), 1):
                if suffix in {'.js', '.jsx', '.ts', '.tsx'}:
                    for match in re.finditer(r'''(?:\bfrom\s*|\brequire\s*\(\s*|\bimport\s*)['"]([^'"\n]+)['"]''', line):
                        finding('import', match.group(1), name, number, 'heuristic')
                route = re.search(r'''(?:@\w+\.(?:route|get|post|put|delete|patch)|\b\w+\.(?:get|post|put|delete|patch))\s*\(\s*['"]([^'"\n]+)''', line)
                if route:
                    finding('route_candidate', route.group(1), name, number, 'heuristic')
                for match in re.finditer(r'https?://[A-Za-z0-9.-]+(?::\d+)?', line):
                    finding('endpoint_host_candidate', match.group(0), name, number, 'heuristic')
    report['summary'] = {'files': len(report['files']), 'bytes': sum(f['bytes'] for f in report['files']), 'languages': dict(Counter(f['language'] for f in report['files'] if f['language'])), 'binary_candidates': sum(f['category'] == 'binary' for f in report['files']), 'findings': len(report['findings'])}
    report['limitations'] = ['Python symbols/imports use AST parsing; JavaScript/TypeScript imports and route/host candidates use heuristics.', 'Other source languages are inventoried only. No complete call graph, runtime behavior, vulnerability audit, or business requirements recovery is claimed.', 'Binary candidates are identified by extension only; decompilation is planned.', 'Nested archives and files over content limits are not analyzed. Endpoint output excludes URL paths, queries and credentials.']
    return report
