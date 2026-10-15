"""Conservative, dependency-free source adapters and local module resolution."""
import ast
import posixpath
import re


def python_details(tree, name, finding):
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is None:
            for alias in node.names:
                finding('import', '.' * node.level + alias.name, name, node.lineno)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                if (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute)
                        and decorator.func.attr in {'route', 'get', 'post', 'put', 'delete', 'patch'}
                        and decorator.args and isinstance(decorator.args[0], ast.Constant)
                        and isinstance(decorator.args[0].value, str)):
                    finding('route_candidate', decorator.args[0].value, name, decorator.lineno, 'heuristic')
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                label = ast.unparse(base)
                if label in {'models.Model', 'db.Model', 'Base', 'DeclarativeBase'}:
                    finding('model_candidate', node.name, name, node.lineno, 'heuristic')


def manifest_details(source, name, finding):
    """Extract names only; never include registry credentials or URL query strings."""
    if name.endswith('requirements.txt'):
        for number, line in enumerate(source.splitlines(), 1):
            match = re.match(r'^\s*([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]*\])?\s*(?:[<>=!~;]|$)', line)
            if match:
                finding('dependency', match.group(1), name, number)
    if name.endswith('go.mod'):
        block = False
        for number, line in enumerate(source.splitlines(), 1):
            clean = line.split('//', 1)[0].strip()
            if clean == 'require (':
                block = True
                continue
            if clean == ')':
                block = False
            match = re.match(r'^(?:require\s+)?([\w.-]+(?:/[\w.-]+)+)\s+v\S+', clean)
            if match and (block or clean.startswith('require ')):
                finding('dependency', match.group(1), name, number)


def resolve_imports(report):
    paths = {f['path'] for f in report['files']}
    dependencies = {f['value'] for f in report['findings'] if f['kind'] == 'dependency'}
    for entry in report['findings']:
        if entry['kind'] not in {'import', 'dependency'}:
            continue
        if entry['kind'] == 'dependency':
            entry['resolution'] = 'external'
            continue
        origin, value = entry['evidence']['file'], entry['value']
        bases = []
        is_python = origin.endswith('.py')
        if is_python:
            if value.startswith('.'):
                dots = len(value) - len(value.lstrip('.'))
                root = posixpath.dirname(origin)
                if dots > len(root.split('/')) or not root:
                    entry['resolution'] = 'unresolved'
                    continue
                for _ in range(dots - 1):
                    root = posixpath.dirname(root)
                bases = [posixpath.join(root, value[dots:].replace('.', '/'))]
            else:
                # Package root is unknown: try ancestor roots, but don't choose ambiguous matches.
                root = posixpath.dirname(origin)
                while True:
                    bases.append(posixpath.join(root, value.replace('.', '/')))
                    if not root:
                        break
                    root = posixpath.dirname(root)
            candidates = [p for base in bases for p in (base + '.py', base + '/__init__.py') if p in paths]
        elif value.startswith('.'):
            base = posixpath.normpath(posixpath.join(posixpath.dirname(origin), value))
            # TypeScript commonly spells emitted .js paths in source imports.
            bases = [base] + ([base[:-3]] if base.endswith('.js') else [])
            candidates = [p for base in bases for p in [base] + [base + ext for ext in ('.ts', '.tsx', '.js', '.jsx', '/index.ts', '/index.tsx', '/index.js', '/index.jsx')] if p in paths]
        else:
            candidates = []
        candidates = sorted(set(candidates))
        if len(candidates) == 1:
            entry.update(resolution='internal', target=candidates[0])
        elif len(candidates) > 1:
            entry.update(resolution='ambiguous', candidates=candidates)
        else:
            package = value.split('/')[0] if not value.startswith('@') else '/'.join(value.split('/')[:2])
            entry['resolution'] = 'external' if package in dependencies and not is_python else 'unresolved'


def compare_reports(current, previous):
    """Compare stable evidence identities; line movement alone is not a new finding."""
    if not isinstance(previous, dict) or previous.get('schema_version') not in (1, 2, 3):
        raise ValueError('Unsupported baseline report schema.')
    if not isinstance(previous.get('files'), list) or not isinstance(previous.get('findings'), list):
        raise ValueError('Baseline must contain files and findings lists.')
    old = {f['path']: f for f in previous['files']}
    new = {f['path']: f for f in current['files']}
    identity = lambda f: (f['kind'], f['value'], f['evidence']['file'])
    old_findings = {identity(f) for f in previous['findings']}
    new_findings = {identity(f) for f in current['findings']}
    changed = sorted(p for p in new.keys() & old.keys() if new[p].get('sha256') and old[p].get('sha256') and new[p]['sha256'] != old[p]['sha256'])
    return {'added_files': sorted(new.keys() - old.keys()), 'removed_files': sorted(old.keys() - new.keys()),
            'changed_files': changed,
            'changed_source_files': [p for p in changed if new[p].get('category') == 'source'],
            'added_findings': [dict(kind=k, value=v, file=p) for k, v, p in sorted(new_findings - old_findings)],
            'removed_findings': [dict(kind=k, value=v, file=p) for k, v, p in sorted(old_findings - new_findings)]}
