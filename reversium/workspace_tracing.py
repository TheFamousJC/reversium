"""Local structural TS/React/Supabase reference graph.

Connections describe lexical source references, including callbacks/branches. They
do not assert execution, authorization, query success or exhaustive type resolution.
"""
import re
from urllib.parse import urlsplit
from .js_tracing import parse_module, arguments
from .feature_map import stable_id

MAX_NODES = 4000
MAX_EDGES = 12000


def trace_workspace(report, sources, sql_sources=None):
    modules, nodes, edges, roots = {}, {}, {}, []
    findings = report['findings']
    gaps = []

    def emit(kind, value, file, line):
        index = len(findings)
        findings.append({'kind': kind, 'value': value[:300], 'confidence': 'static_reference',
                         'evidence': {'file': file, 'line': line}})
        return index

    def node(kind, label, key, evidence=()):
        identity = stable_id(kind, key)
        if identity not in nodes and len(nodes) < MAX_NODES:
            nodes[identity] = {'id': identity, 'kind': kind, 'label': label,
                               'evidence_indices': list(evidence), 'features': [], 'unknowns': []}
        return identity

    def link(source, target, label, file, line, confidence='traced'):
        if source not in nodes or target not in nodes or len(edges) >= MAX_EDGES:
            return
        identity = stable_id('edge', source, target, label)
        if identity not in edges:
            idx = emit('source_reference', nodes[source]['label'] + ' → ' + label + ' → ' + nodes[target]['label'], file, line)
            edges[identity] = {'id': identity, 'source': source, 'target': target, 'label': label,
                               'confidence': confidence, 'evidence_indices': [idx], 'features': []}

    for file, source in sources.items():
        try:
            m = parse_module(source, jsx=file.endswith(('.tsx', '.jsx')))
        except (ValueError, RecursionError) as error:
            gaps.append(f'{file}: structural tracing skipped: {error}.')
            continue
        modules[file] = m
        m.update(file=file, funcs=[], variables=[], imports={})
        m['node'] = node('module', file.split('/')[-1], file)
        t, pairs = m['tokens'], m['pairs']
        # Discover named functions at any lexical depth, including typed props,
        # generic signatures, nested handlers and expression-bodied arrows.
        for i, token in enumerate(t):
            name, param, declaration = None, None, False
            if token.value == 'function' and i + 1 < len(t) and t[i + 1].kind == 'id':
                name, declaration = t[i + 1].value, True
                param = next((j for j in range(i + 2, min(i + 100, len(t))) if t[j].value == '('), None)
            elif token.value == '=>' and i > 0:
                # Locate the nearest parameter list ending before a TS return annotation.
                candidates = [a for a, b in pairs.items() if t[a].value == '(' and b < i and i - b < 60
                              and (b == i - 1 or t[b + 1].value == ':')
                              and all(t[k].value not in (';', '=', '=>') for k in range(b + 1, i))]
                if candidates:
                    param = max(candidates, key=lambda a: pairs[a])
                    before = param - 1
                    if before >= 0 and t[before].value == 'async':
                        before -= 1
                    if before >= 1 and t[before].value == '=':
                        declarations = [k for k in range(max(0, before - 80), before) if t[k].value in ('const', 'let', 'var')
                                        and m['depth'][k] == m['depth'][param]]
                        if declarations:
                            name = t[declarations[-1] + 1].value
                        else:
                            name = '@callback:' + str(token.line) + ':' + str(i)
                    else:
                        name = '@callback:' + str(token.line) + ':' + str(i)
            if name is None or param not in pairs:
                continue
            close = pairs[param]
            if declaration:
                body = close + 1
                while body < len(t) and t[body].value not in ('{', ';', '=>'):
                    body += 1
            else:
                body = i + 1
            if body >= len(t) or t[body].value == ';':
                continue
            if t[body].value == '{' and body in pairs:
                start, end = body + 1, pairs[body]
            else:
                start, end = body, body
                while end < len(t) and t[end].value not in (';', ','):
                    if end in pairs:
                        end = pairs[end]
                    elif t[end].value in (')', '}', ']'):
                        break
                    end += 1
            if any(f['param'] == param for f in m['funcs']):
                continue
            m['funcs'].append({'name': name, 'param': param, 'start': start, 'end': end, 'line': token.line})
        for fn in m['funcs']:
            parents = [f for f in m['funcs'] if f['start'] <= fn['param'] < f['end']]
            fn['parent'] = min(parents, key=lambda f: f['end'] - f['start'], default=None)
            # Anonymous callbacks belong to their enclosing symbol, not fake features.
            if not fn['name'].startswith('@'):
                names, parent = [fn['name']], fn['parent']
                while parent:
                    if not parent['name'].startswith('@'):
                        names.insert(0, parent['name'])
                    parent = parent['parent']
                fn['node'] = node('helper', '.'.join(names), (file, '.'.join(names)))
        for i, token in enumerate(t):
            if token.value in ('const', 'let', 'var') and i + 2 < len(t) and t[i + 1].kind == 'id':
                j = i + 2
                while j < len(t) and t[j].value not in ('=', ';'):
                    if j in pairs:
                        j = pairs[j]
                    j += 1
                if j < len(t) and t[j].value == '=':
                    m['variables'].append((t[i + 1].value, j + 1, enclosing(m, i)))
        for i, token in enumerate(t):
            if token.value != 'import' or m['depth'][i] != 0:
                continue
            j = i + 1
            while j < len(t) and t[j].value not in ('from', ';'):
                j = pairs.get(j, j) + 1
            if j + 1 >= len(t) or t[j].value != 'from' or t[j + 1].kind != 'string':
                continue
            package = t[j + 1].value
            finding = next((f for f in findings if f['kind'] == 'import' and f['evidence']['file'] == file and f['value'] == package), {})
            target = finding.get('target') if finding.get('resolution') == 'internal' else None
            if i + 1 < j and t[i + 1].kind == 'id' and t[i + 1].value != 'type':
                m['imports'][t[i + 1].value] = (target, 'default', package)
            brace = next((k for k in range(i + 1, j) if t[k].value == '{'), None)
            if brace is not None:
                for a, b in arguments(m, brace):
                    if t[a].value == 'type':
                        a += 1
                    original = t[a].value
                    alias = t[a + 2].value if a + 2 < b and t[a + 1].value == 'as' else original
                    m['imports'][alias] = (target, original, package)
        for item in report['files']:
            if item['path'] == file:
                item['analysis'] = 'jsx_reference_scan' if file.endswith(('.tsx', '.jsx')) else 'js_token_scan'
                break

    def scopes(m, pos):
        owner = enclosing(m, pos)
        result = []
        while owner:
            result.append(owner)
            owner = owner['parent']
        return result + [None]

    def symbol(m, name, pos):
        for scope in scopes(m, pos):
            if scope:
                for a, b in arguments(m, scope['param']):
                    if m['tokens'][a].value == name:
                        return None
            matches = [f for f in m['funcs'] if f['name'] == name and f['parent'] is scope]
            if len(matches) == 1:
                return m, matches[0]
            if len(matches) > 1:
                return None
            if any(n == name and owner is scope for n, a, owner in m['variables']):
                return None
        binding = m['imports'].get(name)
        if binding and binding[0] in modules:
            other = modules[binding[0]]
            choices = [f for f in other['funcs'] if f['parent'] is None and
                       (f['name'] == binding[1] or binding[1] == 'default' and f['name'][0].isupper())]
            if len(choices) == 1:
                return other, choices[0]
        return None

    def client(m, name, pos, seen=None):
        seen = set() if seen is None else seen
        key = (m['file'], name, pos)
        if key in seen or len(seen) >= 12:
            return None
        seen.add(key)
        for scope in scopes(m, min(pos, len(m['tokens']) - 1)):
            if scope:
                for a, b in arguments(m, scope['param']):
                    if m['tokens'][a].value == name:
                        type_names = {m['tokens'][k].value for k in range(a + 1, b)}
                        if any(alias in type_names and imp[2] == '@supabase/supabase-js' and imp[1] == 'SupabaseClient'
                               for alias, imp in m['imports'].items()):
                            return 'supabase'
                        return None  # Parameter shadows a global client.
            matches = [a for n, a, owner in m['variables'] if n == name and owner is scope]
            if len(matches) == 1:
                start = matches[0]
                t = m['tokens']
                # Conditional initializers are candidate factories, never proven setup.
                end = start
                while end < len(t) and t[end].value != ';':
                    end = m['pairs'].get(end, end) + 1
                for k in range(start, min(end, start + 120)):
                    if t[k].kind == 'id' and m['depth'][k] == m['depth'][start] and k + 1 < len(t) and t[k + 1].value == '(':
                        factory = client(m, t[k].value, k, seen.copy())
                        if factory == 'supabase-factory':
                            return 'supabase'
                        if factory == 'router-factory':
                            return 'router'
                        called = symbol(m, t[k].value, k)
                        if called:
                            cm, fn = called
                            # Only direct factory returns, not arbitrary calls in body.
                            for q in range(fn['start'], fn['end'] - 2):
                                if cm['tokens'][q].value == 'return' and cm['tokens'][q + 2].value == '(' and enclosing(cm, q) is fn:
                                    returned = client(cm, cm['tokens'][q + 1].value, q, seen.copy())
                                    if returned == 'supabase-factory':
                                        return 'supabase'
                if start < len(t) and t[start].kind == 'id':
                    return client(m, t[start].value, start, seen)
                return None
            if matches:
                return None
        binding = m['imports'].get(name)
        if binding:
            target, original, package = binding
            if package == '@supabase/supabase-js' and original == 'createClient':
                return 'supabase-factory'
            if package == 'express' and original in ('Router', 'default'):
                return 'router-factory'
            if target in modules:
                return client(modules[target], original, len(modules[target]['tokens']), seen)
        return None

    routes, requests, mounts = [], [], []
    for file, m in modules.items():
        t, pairs = m['tokens'], m['pairs']
        def owner(pos):
            fn = enclosing(m, pos)
            while fn and 'node' not in fn:
                fn = fn['parent']
            return fn.get('node', m['node']) if fn else m['node']

        for alias, (target, original, package) in m['imports'].items():
            if target in modules:
                link(m['node'], modules[target]['node'], 'imports', file,
                     next((f['evidence']['line'] for f in findings if f['kind'] == 'import' and f['value'] == package and f['evidence']['file'] == file), 1))
        if file.endswith(('.tsx', '.jsx')):
            idx = emit('react_module', 'React/JSX module: ' + file.split('/')[-1], file, 1)
            roots.append({'node': m['node'], 'name': 'UI ' + file.split('/')[-1], 'file': file, 'evidence_indices': [idx], 'type': 'react'})
            for fn in m['funcs']:
                if fn['parent'] is None and 'node' in fn:
                    link(m['node'], fn['node'], 'declares', file, fn['line'])
        for i, token in enumerate(t):
            if token.kind == 'jsx':
                target = m['imports'].get(token.value)
                if target and target[0] in modules:
                    link(owner(i), modules[target[0]]['node'], 'JSX reference', file, token.line)
                else:
                    found = symbol(m, token.value, i)
                    if found and 'node' in found[1]:
                        link(owner(i), found[1]['node'], 'JSX reference', file, token.line)
                continue
            if token.kind == 'jsx-ref':
                found = symbol(m, token.value, i)
                if found and 'node' in found[1]:
                    link(owner(i), found[1]['node'], 'JSX value reference', file, token.line)
                continue
            if token.kind != 'id' or i and t[i - 1].value in ('.', '?.', 'function', 'new'):
                continue
            # Direct named helper calls, including callbacks/branches. Declaration
            # parameter lists must never become self-calls.
            if i + 1 < len(t) and t[i + 1].value == '(' and not any(f['param'] == i + 1 for f in m['funcs']):
                found = symbol(m, token.value, i)
                if found and 'node' in found[1]:
                    link(owner(i), found[1]['node'], 'call reference', file, token.line)
            # Collect a member/call chain while skipping argument bodies.
            j, chain = i + 1, []
            while j + 2 < len(t) and t[j].value in ('.', '?.', '!'):
                if t[j].value == '!':
                    j += 1
                    continue
                member = t[j + 1].value
                if t[j + 2].value == '(' and j + 2 in pairs:
                    chain.append((member, arguments(m, j + 2), j + 2))
                    j = pairs[j + 2] + 1
                else:
                    chain.append((member, [], None))
                    j += 2
            if not chain:
                continue
            receiver = client(m, token.value, i)
            if receiver == 'router' and chain[0][0] == 'use':
                args = chain[0][1]
                if args and args[0][1] == args[0][0] + 1 and t[args[0][0]].kind == 'string':
                    prefix = t[args[0][0]].value
                    for a, b in args[1:]:
                        if a + 1 < b and t[a + 1].value == '(':
                            found = symbol(m, t[a].value, i)
                            if found:
                                mounts.append((found[0]['file'], found[1]['name'], prefix, file, token.line))
            if receiver == 'router' and chain[0][0] in ('get', 'post', 'put', 'patch', 'delete'):
                method, args, call = chain[0]
                if len(args) < 2:
                    continue
                a, b = args[0]
                paths = [t[a].value] if b == a + 1 and t[a].kind == 'string' else []
                if t[a].value == '[' and a in pairs:
                    paths = [t[x].value for x, y in arguments(m, a) if y == x + 1 and t[x].kind == 'string']
                callback = next((f for f in m['funcs'] if args[-1][0] <= f['param'] < args[-1][1]), None)
                target = owner(i)
                if callback:
                    registration = enclosing(m, i)
                    callback['node'] = node('handler', method.upper() + ' handler ' + (paths[0] if paths else '?'), (file, registration['name'] if registration else '', method, tuple(paths)))
                    target = callback['node']
                elif args[-1][1] == args[-1][0] + 1:
                    found = symbol(m, t[args[-1][0]].value, i)
                    if found and 'node' in found[1]:
                        target = found[1]['node']
                for path in paths:
                    idx = emit('route_reference', method.upper() + ' ' + path, file, token.line)
                    route = node('feature', method.upper() + ' ' + path, (file, method, path), [idx])
                    link(route, target, 'handler reference', file, token.line)
                    roots.append({'node': route, 'name': method.upper() + ' ' + path, 'registered_path': path, 'file': file, 'evidence_indices': [idx], 'type': 'route'})
                    scope = enclosing(m, i)
                    routes.append((path, route, file, scope['name'] if scope else None))
            if receiver != 'supabase':
                continue
            names = [name for name, _, _ in chain]
            if names[0] == 'from' and chain[0][1]:
                a, b = chain[0][1][0]
                if b == a + 1 and t[a].kind == 'string':
                    actions = [n for n in names[1:] if n in ('select', 'insert', 'update', 'upsert', 'delete')]
                    action = next((n for n in actions if n != 'select'), 'select' if 'select' in actions else 'query')
                    resource = node('data', 'Supabase: ' + t[a].value, ('Supabase', t[a].value))
                    link(owner(i), resource, {'select': 'reads', 'insert': 'adds', 'update': 'updates', 'upsert': 'upserts', 'delete': 'deletes', 'query': 'query reference'}[action], file, token.line, 'inferred')
                else:
                    gaps.append(f'{file}:{token.line}: dynamic Supabase table is unresolved.')
            elif names[0] == 'rpc' and chain[0][1]:
                a, b = chain[0][1][0]
                if b == a + 1 and t[a].kind == 'string':
                    resource = node('rpc', 'RPC: ' + t[a].value, ('Supabase RPC', t[a].value))
                    link(owner(i), resource, 'RPC reference', file, token.line, 'inferred')
                else:
                    gaps.append(f'{file}:{token.line}: dynamic Supabase RPC is unresolved.')
            elif names[0] == 'storage':
                buckets = [args for name, args, _ in chain if name == 'from' and args]
                bucket = None
                if buckets:
                    a, b = buckets[0][0]
                    if b == a + 1 and t[a].kind == 'string':
                        bucket = t[a].value
                resource = node('storage', 'Storage: ' + (bucket or 'dynamic bucket'), ('Supabase storage', bucket or file))
                link(owner(i), resource, 'storage ' + names[-1], file, token.line, 'inferred')
            elif names[0] == 'auth':
                resource = node('auth', 'Supabase Auth', 'Supabase Auth')
                link(owner(i), resource, 'auth ' + '.'.join(names[1:]), file, token.line)

        # fetch references: only literal local paths or literal/template hosts.
        for i, token in enumerate(t[:-2]):
            if token.value != 'fetch' or t[i + 1].value != '(' or i + 1 not in pairs or (i and t[i - 1].value in ('.', 'function')):
                continue
            args = arguments(m, i + 1)
            if not args:
                continue
            a, b = args[0]
            if b != a + 1 or t[a].kind not in ('string', 'dynamic'):
                gaps.append(f'{file}:{token.line}: fetch target is computed; endpoint unresolved.')
                continue
            value = t[a].value
            if value.startswith('/') and not value.startswith('//'):
                path = value.split('?')[0]
                # Template paths are displayed as candidates, not matched to routes.
                if t[a].kind == 'string':
                    requests.append((owner(i), path, file, token.line))
                else:
                    gaps.append(f'{file}:{token.line}: templated local API target is unresolved.')
            elif value.startswith(('https://', 'http://')):
                try:
                    host = urlsplit(value).hostname
                    if host and '${' not in host:
                        resource = node('external', host, host)
                        link(owner(i), resource, 'fetch host reference', file, token.line)
                except ValueError:
                    pass
    for path, route, file, scope in routes:
        candidates = [mount for mount in mounts if mount[:2] == (file, scope)]
        if len({mount[2] for mount in candidates}) == 1:
            mount = candidates[0]
            prefix = mount[2].rstrip('/')
            mounted = prefix + '/' + path.lstrip('/')
            nodes[route]['label'] = nodes[route]['label'].split(' ', 1)[0] + ' ' + mounted
            idx = emit('router_mount_candidate', prefix + ' → ' + scope, mount[3], mount[4])
            nodes[route]['evidence_indices'].append(idx)
            for root in roots:
                if root['node'] == route:
                    root['name'] = nodes[route]['label']
                    root['evidence_indices'].append(idx)
        elif candidates:
            gaps.append(f'{file}: multiple router mounts; effective paths remain unknown.')
    for caller, path, file, line in requests:
        matches = [(route, rf) for rp, route, rf, scope in routes if nodes[route]['label'].split(' ', 1)[1] == path]
        if len(matches) == 1:
            link(caller, matches[0][0], 'local API path candidate', file, line, 'inferred')
        else:
            resource = node('external', 'Local API: ' + path[:100], ('local-api', path))
            link(caller, resource, 'local fetch reference', file, line)
    # Include a module's named declarations so imported modules remain navigable.
    for file, m in modules.items():
        for fn in m['funcs']:
            if fn['parent'] is None and 'node' in fn:
                link(m['node'], fn['node'], 'declares', file, fn['line'])
    # Match literal RPC names to migration definitions. This is a name-based
    # candidate across files, never confirmation a migration was applied.
    declared_tables = set()
    for source in (sql_sources or {}).values():
        declared_tables.update(re.findall(r'\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:public\.)?([A-Za-z_]\w*)', source, re.I))
    for file, source in (sql_sources or {}).items():
        clean = re.sub(r"'(?:''|[^'])*'|--[^\n]*|/\*.*?\*/", lambda m: ''.join('\n' if c == '\n' else ' ' for c in m.group()), source, flags=re.S)
        pattern = r'\bCREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+(?:public\.)?([A-Za-z_]\w*)\s*\('
        for definition in re.finditer(pattern, clean, re.I):
            next_definition = re.search(pattern, clean[definition.end():], re.I)
            boundary = definition.end() + next_definition.start() if next_definition else len(clean)
            opening = re.search(r'\bAS\s+(\$\w*\$)', clean[definition.end():boundary], re.I)
            if not opening:
                continue
            start = definition.end() + opening.end()
            end = clean.find(opening.group(1), start)
            if end < 0 or end > boundary:
                continue
            resource = node('rpc', 'RPC: ' + definition.group(1), ('Supabase RPC', definition.group(1)))
            idx = emit('sql_function_candidate', definition.group(1), file, clean[:definition.start()].count('\n') + 1)
            if resource in nodes:
                nodes[resource]['evidence_indices'].append(idx)
            for match in re.finditer(r'\b(FROM|JOIN|INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+(public\.)?([A-Za-z_]\w*)', clean[start:end], re.I):
                # Function calls in FROM are RPC/function references, not tables.
                following = clean[start + match.end():end].lstrip()
                if match.group(1).upper() in ('FROM', 'JOIN') and following.startswith('('):
                    continue
                table = match.group(3)
                if table.lower() in {'set', 'select', 'where', 'excluded'} or not match.group(2) and table not in declared_tables:
                    continue
                target = node('data', 'Supabase: ' + table, ('Supabase', table))
                verb = match.group(1).upper()
                label = 'SQL ' + ('adds' if verb.startswith('INSERT') else 'updates' if verb == 'UPDATE' else 'deletes' if verb.startswith('DELETE') else 'reads') + ' candidate'
                link(resource, target, label, file, clean[:start + match.start()].count('\n') + 1, 'inferred')
    report['workspace_graph'] = {'nodes': list(nodes.values()), 'edges': list(edges.values()), 'roots': roots,
                                 'mount_candidates': mounts,
                                 'parsed_files': len(modules), 'gaps': list(dict.fromkeys(gaps))[:200],
                                 'limits': {'nodes': MAX_NODES, 'edges': MAX_EDGES}}
    if len(nodes) >= MAX_NODES or len(edges) >= MAX_EDGES:
        report['warnings'].append('Workspace reference graph reached its 4,000 node / 12,000 edge cap.')
    report['warnings'].extend(list(dict.fromkeys(gaps))[:200])


def enclosing(module, pos):
    return min((f for f in module['funcs'] if f['start'] <= pos < f['end']),
               key=lambda f: f['end'] - f['start'], default=None)
