"""Bounded Python route/helper tracing. Describes syntax, never executes code."""
import ast
import re
from itertools import islice

MAX_ROUTES = 100
MAX_FUNCTIONS = 12
MAX_DEPTH = 3
MAX_OPERATIONS = 40
MAX_NODES = 10000


def body_nodes(function):
    """Exclude nested definitions: declaring a function does not call its body."""
    pending = list(reversed(function.body))
    while pending:
        node = pending.pop()
        yield node
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            pending.extend(reversed(list(ast.iter_child_nodes(node))))


def trace_routes(report, trees):
    findings = report['findings']
    imports = {(f['evidence']['file'], f['evidence'].get('line'), f['value']): f.get('target') for f in findings if f['kind'] == 'import' and f.get('resolution') == 'internal'}
    modules = {}
    for file, tree in trees.items():
        functions, names = {}, {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.setdefault(node.name, []).append(node)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    target = imports.get((file, node.lineno, alias.name))
                    names[alias.asname or alias.name.split('.')[0]] = ('module', target) if target else alias.name
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    value = '.' * node.level + (node.module or alias.name)
                    target = imports.get((file, node.lineno, value))
                    names[alias.asname or alias.name] = ('function', target, alias.name) if target and node.module else ('module', target) if target else (node.module or '') + '.' + alias.name
        for name, definitions in functions.items():
            names[name] = ('function', file, name) if len(definitions) == 1 else None
        # Reassigned module names cannot be resolved reliably.
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name):
                        names[target.id] = None
        modules[file] = (functions, names)

    def symbol(node, context, depth=0):
        if depth > 24:
            return None
        if isinstance(node, ast.Name):
            return context.get(node.id)
        if isinstance(node, ast.Attribute):
            parent = symbol(node.value, context, depth + 1)
            if isinstance(parent, tuple) and parent[0] == 'module':
                return ('function', parent[1], node.attr)
            if isinstance(parent, str):
                return parent + '.' + node.attr
        if isinstance(node, ast.Call) and symbol(node.func, context, depth + 1) in ('sqlite-connection.execute', 'sqlite-connection.executemany', 'sqlite-cursor.execute', 'sqlite-cursor.executemany', 'sqlite-connection.cursor'):
            return 'sqlite-cursor'
        return None

    def emit(kind, value, file, line):
        index = len(findings)
        findings.append({'kind': kind, 'value': value[:300], 'confidence': 'static_trace', 'evidence': {'file': file, 'line': line}})
        return index

    traces = []
    for file, tree in trees.items():
        for function in tree.body:
            if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in function.decorator_list:
                if not (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute) and decorator.func.attr in {'get', 'post', 'put', 'delete', 'patch', 'route'} and decorator.args and isinstance(decorator.args[0], ast.Constant) and isinstance(decorator.args[0].value, str)):
                    continue
                if len(traces) >= MAX_ROUTES:
                    report['warnings'].append('Python route tracing capped at 100 routes.')
                    report['route_traces'] = traces
                    return
                path = decorator.args[0].value
                method = decorator.func.attr.upper()
                trace = {'route': path, 'method': method if method != 'ROUTE' else 'method unspecified', 'handler': function.name,
                         'operations': [], 'unknowns': [], 'evidence_indices': [emit('route_handler', f'{path} → {function.name}', file, decorator.lineno)]}
                visited = set()

                def operation(text, current_file, line):
                    if len(trace['operations']) >= MAX_OPERATIONS:
                        trace['unknowns'].append('Operation limit reached (40).')
                        return
                    index = emit('handler_operation', text, current_file, line)
                    trace['operations'].append({'description': text, 'evidence_index': index})

                def visit(current_file, current_function, depth, bindings=None):
                    key = (current_file, current_function.name)
                    if key in visited:
                        trace['unknowns'].append('Repeated or recursive helper calls were not expanded again.')
                        return
                    if depth > MAX_DEPTH or len(visited) >= MAX_FUNCTIONS:
                        trace['unknowns'].append('Helper tracing reached its depth/function limit (3 levels / 12 functions).')
                        return
                    visited.add(key)
                    context = dict(modules[current_file][1])
                    nodes = list(islice(body_nodes(current_function), MAX_NODES + 1))
                    if len(nodes) > MAX_NODES:
                        nodes = nodes[:MAX_NODES]
                        trace['unknowns'].append('Function syntax scan capped at 10,000 nodes.')
                    parameters = current_function.args.posonlyargs + current_function.args.args + current_function.args.kwonlyargs
                    for parameter in parameters:
                        context[parameter.arg] = (bindings or {}).get(parameter.arg)
                    # Unknown assignments shadow imports/helper names. Repeated assignments stay unknown.
                    assignments = {}
                    for node in nodes:
                        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                            context[node.id] = None
                        elif isinstance(node, (ast.Import, ast.ImportFrom)):
                            for alias in node.names:
                                context[alias.asname or alias.name.split('.')[0]] = None
                        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                            for target in targets:
                                if isinstance(target, ast.Name):
                                    assignments.setdefault(target.id, []).append(node)
                                    context[target.id] = None
                        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                            context[node.name] = None
                    for name, values in assignments.items():
                        if len(values) != 1:
                            continue
                        value = getattr(values[0], 'value', None)
                        if isinstance(value, ast.Call) and symbol(value.func, context) == 'sqlite3.connect':
                            context[name] = 'sqlite-connection'
                        elif isinstance(value, ast.Call) and symbol(value.func, context) == 'sqlite-connection.cursor':
                            context[name] = 'sqlite-cursor'
                        elif isinstance(value, ast.Call) and symbol(value.func, context) == 'sqlite-cursor.fetchall':
                            context[name] = 'sqlite-rows'
                    for node in nodes:
                        if isinstance(node, ast.Return):
                            value = node.value
                            if isinstance(value, ast.Dict):
                                fields = [str(k.value) for k in value.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)]
                                operation('Returns a structured response with fields: ' + ', '.join(fields[:12]) + '.' if fields else 'Returns a structured response.', current_file, node.lineno)
                            elif isinstance(value, (ast.List, ast.ListComp)):
                                operation('Returns a list of results.', current_file, node.lineno)
                            elif symbol(value, context) == 'sqlite-rows' or (isinstance(value, ast.Call) and symbol(value.func, context) == 'sqlite-cursor.fetchall'):
                                operation('Returns rows read from the database.', current_file, node.lineno)
                            elif isinstance(value, ast.Constant):
                                operation('Returns a fixed value (content omitted).', current_file, node.lineno)
                        if not isinstance(node, ast.Call):
                            continue
                        target = symbol(node.func, context)
                        if isinstance(target, tuple) and target[0] == 'function':
                            helper_file, helper_name = target[1:]
                            definitions = modules.get(helper_file, ({}, {}))[0].get(helper_name, [])
                            if len(definitions) == 1:
                                helper = definitions[0]
                                if len(trace['evidence_indices']) >= MAX_FUNCTIONS * 2:
                                    trace['unknowns'].append('Helper-call evidence limit reached (24).')
                                    continue
                                trace['evidence_indices'].append(emit('handler_call', f'{current_function.name} → {helper_name}', current_file, node.lineno))
                                args = helper.args.posonlyargs + helper.args.args
                                passed = {param.arg: symbol(arg, context) for param, arg in zip(args, node.args)}
                                passed.update({kw.arg: symbol(kw.value, context) for kw in node.keywords if kw.arg})
                                visit(helper_file, helper, depth + 1, passed)
                                continue
                        if isinstance(node.func, ast.Attribute) and node.func.attr in {'execute', 'executemany'} and symbol(node.func.value, context) in {'sqlite-connection', 'sqlite-cursor'}:
                            sql = node.args[0] if node.args else None
                            if isinstance(sql, ast.Constant) and isinstance(sql.value, str):
                                clean = re.sub(r"'(?:''|[^'])*'", "''", sql.value)
                                clean = re.sub(r'/\*.*?\*/|--[^\n]*', ' ', clean, flags=re.S)
                                match = re.match(r'\s*(SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM)\b', clean, re.I) if ';' not in clean.strip().rstrip(';') else None
                                if match:
                                    action = match.group(1).upper().split()[0]
                                    table = re.search(r'\b(?:FROM|INTO|UPDATE)\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)?)', clean, re.I)
                                    verb = {'SELECT': 'Reads', 'INSERT': 'Adds', 'UPDATE': 'Updates', 'DELETE': 'Deletes'}[action]
                                    description = verb + ' records in “' + table.group(1) + '” via SQLite.' if table else 'Contains a SQLite ' + action + ' statement; no table was identified.'
                                    operation(description, current_file, node.lineno)
                                else:
                                    trace['unknowns'].append('A SQL statement is present but its operation is unsupported.')
                            else:
                                trace['unknowns'].append('Dynamic SQL could not be interpreted.')
                        elif target in ('sqlite-connection.commit', 'sqlite-cursor.commit'):
                            operation('Requests that pending database changes be committed.', current_file, node.lineno)
                        elif target == 'sqlite3.connect':
                            operation('Opens a SQLite database connection.', current_file, node.lineno)
                        elif target in ('sqlite-connection.cursor',):
                            pass
                        elif not (isinstance(target, str) and target.startswith('sqlite-') and getattr(node.func, 'attr', '') in {'fetchall', 'fetchone', 'close'}):
                            trace['unknowns'].append(f'Call on line {node.lineno} of {current_file} was not resolved to a supported operation.')
                    if current_function.decorator_list and depth:
                        trace['unknowns'].append('Helper decorators may change behavior; their effects are not traced.')

                visit(file, function, 0)
                trace['unknowns'] += ['Statements may be conditional or unreachable; branch outcomes, call order, authorization and successful execution are not verified.',
                                      'Only supported Python module-level handlers/helpers and SQLite operations are traced. ORM operations and other languages remain untraced.']
                trace['unknowns'] = list(dict.fromkeys(trace['unknowns']))
                trace['evidence_indices'] += [item['evidence_index'] for item in trace['operations']]
                traces.append(trace)
    report['route_traces'] = traces
