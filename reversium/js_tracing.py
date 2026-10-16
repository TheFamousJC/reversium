"""Conservative JS/TS token tracer: Express routes and pg/mysql2 literal SQL.

Not a full language parser. Unsupported or ambiguous constructs remain unknown.
No source is evaluated and no Node.js runtime is required.
"""
import re
from dataclasses import dataclass

TOKEN = re.compile(r'[A-Za-z_$][\w$]*|\d+(?:\.\d+)?|=>|===|!==|\?\.|==|!=|&&|\|\|')


@dataclass
class Token:
    value: str
    kind: str
    line: int


def tokenize(source, jsx=False):
    output, i, line = [], 0, 1
    while i < len(source):
        if len(output) >= 60000:
            raise ValueError('token limit (60,000)')
        char = source[i]
        if jsx and char == '<' and re.match(r'<(?:[A-Za-z_$]|>)', source[i:]) and not re.match(r'<[^<>\n]+>\s*\(', source[i:]) and (not output or output[-1].value in {'return', '(', '=', '=>', '&&', '||', '?', ':', '{', ','}):
            from .jsx import jsx_tokens
            extra, consumed = jsx_tokens(source[i:], tokenize)
            output.extend(Token(t.value, t.kind, t.line + line - 1) for t in extra)
            line += source[i:i + consumed].count('\n')
            i += consumed
            continue
        if char.isspace():
            line += char == '\n'
            i += 1
            continue
        if source.startswith('//', i):
            end = source.find('\n', i)
            i = len(source) if end < 0 else end
            continue
        if source.startswith('/*', i):
            end = source.find('*/', i + 2)
            if end < 0:
                raise ValueError('unterminated comment')
            line += source[i:end + 2].count('\n')
            i = end + 2
            continue
        if char in '\'"`':
            quote, start, content = char, line, []
            i += 1
            while i < len(source) and source[i] != quote:
                if source[i] == '\\' and i + 1 < len(source):
                    i += 1
                    content.append({'n': '\n', 'r': '\r', 't': '\t'}.get(source[i], source[i]))
                else:
                    content.append(source[i])
                line += source[i] == '\n'
                i += 1
            if i >= len(source):
                raise ValueError('unterminated string/template')
            i += 1
            value = ''.join(content)
            output.append(Token(value, 'dynamic' if quote == '`' and '${' in value else 'string', start))
            continue
        # Consume regex bodies as opaque literals. Their text must never become code.
        if char == '/' and (not output or output[-1].value in {'=', '(', ',', ':', 'return', '=>', '[', '!', '&&', '||', '?'}):
            start, bracket = line, False
            i += 1
            while i < len(source):
                if source[i] == '\n':
                    raise ValueError('unterminated regular-expression literal')
                if source[i] == '\\':
                    i += 2
                    continue
                if source[i] == '[':
                    bracket = True
                elif source[i] == ']':
                    bracket = False
                elif source[i] == '/' and not bracket:
                    i += 1
                    while i < len(source) and source[i].isalpha():
                        i += 1
                    break
                i += 1
            else:
                raise ValueError('unterminated regular-expression literal')
            output.append(Token('', 'regex', start))
            continue
        match = TOKEN.match(source, i)
        value = match.group() if match else char
        output.append(Token(value, 'id' if value[0].isalpha() or value[0] in '_$' else 'punct', line))
        i += len(value)
    if len(output) > 60000:
        raise ValueError('token limit (60,000)')
    return output


def parse_module(source, jsx=False):
    tokens = tokenize(source, jsx=jsx)
    pairs, stack, depth = {}, [], {}
    for i, token in enumerate(tokens):
        depth[i] = len(stack)
        if token.kind != 'punct':
            continue
        if token.value in ('(', '{', '['):
            stack.append((token.value, i))
        elif token.value in (')', '}', ']'):
            if not stack or stack[-1][0] != {')': '(', '}': '{', ']': '['}[token.value]:
                raise ValueError('unbalanced syntax')
            _, start = stack.pop()
            pairs[start] = i
    if stack:
        raise ValueError('unclosed syntax')
    return {'tokens': tokens, 'pairs': pairs, 'depth': depth, 'functions': {}, 'bindings': {}, 'assignments': {}, 'shadowed': set()}


def arguments(module, start):
    tokens, pairs = module['tokens'], module['pairs']
    end, parts, current, i = pairs[start], [], start + 1, start + 1
    while i < end:
        if tokens[i].value == ',' and tokens[i].kind == 'punct':
            parts.append((current, i))
            current = i + 1
        elif i in pairs:
            i = pairs[i]
        i += 1
    if current < end:
        parts.append((current, end))
    return parts


def function_at(module, start, end, name):
    t, pairs = module['tokens'], module['pairs']
    i = start
    if i < end and t[i].value == 'async':
        i += 1
    declaration = i < end and t[i].value == 'function'
    if i < end and t[i].value == 'function':
        i += 1
        if i < end and t[i].kind == 'id':
            i += 1
    if i >= end or t[i].value != '(' or i not in pairs:
        return None
    params = []
    for a, b in arguments(module, i):
        if a >= b or t[a].kind != 'id' or any(t[k].value in ('{', '[', '...') for k in range(a, min(b, a + 2))):
            return None
        params.append(t[a].value)
    close = pairs[i]
    j = close + 1
    while j < end and t[j].value not in ('{', '=>', ';', '='):
        j += 1
    if j < end and t[j].value == '=>':
        j += 1
    elif not declaration:
        return None
    if j >= end or t[j].value != '{' or j not in pairs:
        return None
    return {'name': name, 'params': params, 'start': j + 1, 'end': pairs[j], 'line': t[start].line}


def trace_javascript(report, sources):
    modules = {}
    for file, source in sources.items():
        try:
            module = parse_module(source)
        except ValueError as error:
            report['warnings'].append(f'{file}: JS/TS tracing skipped: {error}. Import/route heuristics may still be present.')
            continue
        modules[file] = module
        for item in report['files']:
            if item['path'] == file:
                item['analysis'] = 'js_token_scan'
                break
        t, pairs, depth = module['tokens'], module['pairs'], module['depth']
        bindings = module['bindings']
        for i, token in enumerate(t):
            if depth[i] != 0:
                continue
            if token.kind == 'id' and i + 1 < len(t) and t[i + 1].value == '=' and (i == 0 or t[i - 1].value not in ('const', 'let', 'var', '.', ':')):
                module['shadowed'].add(token.value)
            if token.value == 'import':
                j = i + 1
                while j < len(t) and t[j].value not in ('from', ';'):
                    j = pairs.get(j, j) + 1
                if j + 1 < len(t) and t[j].value == 'from' and t[j + 1].kind == 'string':
                    package = t[j + 1].value
                    target = next((f.get('target') for f in report['findings'] if f['kind'] == 'import' and f['evidence']['file'] == file and f['value'] == package and f.get('resolution') == 'internal'), None)
                    if i + 1 < j and t[i + 1].value == '{':
                        for a, b in arguments_like_braces(module, i + 1):
                            original = t[a].value
                            alias = t[a + 2].value if a + 2 < b and t[a + 1].value == 'as' else original
                            bindings[alias] = ('import', target, original) if target else package + '.' + original
                    elif i + 1 < j and t[i + 1].kind == 'id':
                        bindings[t[i + 1].value] = ('import', target, 'default') if target else package
            if token.value == 'function' and i + 2 < len(t) and t[i + 1].kind == 'id':
                name = t[i + 1].value
                function = function_at(module, i, len(t), name)
                if function:
                    module['functions'].setdefault(name, []).append(function)
            if token.value in ('const', 'let', 'var') and i + 1 < len(t) and t[i + 1].kind == 'id':
                name, j = t[i + 1].value, i + 2
                while j < len(t) and t[j].value not in ('=', ';'):
                    j += 1
                if j < len(t) and t[j].value == '=':
                    module['assignments'].setdefault(name, []).append(j + 1)
                    if name in bindings:
                        module['shadowed'].add(name)
                    function = function_at(module, j + 1, len(t), name)
                    if function:
                        module['functions'].setdefault(name, []).append(function)

    def lookup(file, name, context=None, seen=None):
        seen = set() if seen is None else seen
        if (file, name) in seen or len(seen) > 12 or file not in modules:
            return None
        seen.add((file, name))
        module = modules[file]
        if name in module['shadowed']:
            return None
        if context is not None and name in context:
            return context[name]
        definitions = module['functions'].get(name, [])
        if len(definitions) == 1:
            return ('function', file, name)
        value = module['bindings'].get(name)
        if isinstance(value, tuple):
            return lookup(value[1], value[2], seen=seen)
        if value:
            return value
        assignments = module['assignments'].get(name, [])
        if len(assignments) == 1:
            return expression(file, assignments[0], None, seen)[0]
        return None

    def expression(file, start, context=None, seen=None, depth=0):
        module = modules[file]
        t, pairs = module['tokens'], module['pairs']
        if start >= len(t) or depth > 16:
            return None, start
        i = start
        if t[i].value in ('await', 'new'):
            i += 1
        if i >= len(t) or t[i].kind != 'id':
            return None, i
        value = lookup(file, t[i].value, context, seen)
        i += 1
        while i < len(t):
            if t[i].value == '.' and i + 1 < len(t):
                value = value + '.' + t[i + 1].value if isinstance(value, str) else None
                i += 2
            elif t[i].value == '(' and i in pairs:
                if value in ('express', 'express.Router'):
                    value = 'express-router'
                elif value in ('pg.Pool', 'pg.Client'):
                    value = 'pg-client'
                elif value in ('mysql2.createPool', 'mysql2/promise.createPool', 'mysql2.createConnection', 'mysql2/promise.createConnection'):
                    value = 'mysql-client'
                elif value in ('response.status',):
                    value = 'response'
                else:
                    value = None
                i = pairs[i] + 1
            else:
                break
        return value, i

    def emit(kind, value, file, line, **extra):
        index = len(report['findings'])
        report['findings'].append({'kind': kind, 'value': value[:300], 'confidence': 'bounded_token_trace', 'evidence': {'file': file, 'line': line}, **extra})
        return index

    for file, module in modules.items():
        t, pairs = module['tokens'], module['pairs']
        for i in range(len(t) - 3):
            if module['depth'][i] != 0 or t[i].kind != 'id' or t[i + 1].value != '.' or t[i + 2].value not in ('get', 'post', 'put', 'patch', 'delete') or t[i + 3].value != '(':
                continue
            if lookup(file, t[i].value) != 'express-router' or i + 3 not in pairs:
                continue
            parts = arguments(module, i + 3)
            if len(parts) < 2 or t[parts[0][0]].kind != 'string':
                continue
            a, b = parts[-1]
            function = function_at(module, a, b, f'inline@{t[a].line}')
            owner_file = file
            if not function and b == a + 1:
                resolved = lookup(file, t[a].value)
                if isinstance(resolved, tuple) and resolved[0] == 'function':
                    owner_file = resolved[1]
                    function = modules[owner_file]['functions'][resolved[2]][0]
            if not function:
                report['warnings'].append(f'{file}:{t[i].line}: route callback is outside supported JS/TS syntax.')
                continue
            if len(report['route_traces']) >= 100:
                report['warnings'].append('Combined Python/JS route tracing capped at 100 routes.')
                return
            path = t[parts[0][0]].value
            if function['name'].startswith('inline@'):
                function = dict(function, name='inline ' + t[i + 2].value.upper() + ' ' + path)
            trace = {'route': path, 'method': t[i + 2].value.upper(), 'handler': function['name'], 'handler_file': owner_file, 'operations': [], 'evidence_indices': [emit('route_handler', path + ' → ' + function['name'], file, t[i].line)], 'unknowns': []}
            visited = set()

            def note(text):
                if len(trace['unknowns']) < 26:
                    trace['unknowns'].append(text)
                elif len(trace['unknowns']) == 26:
                    trace['unknowns'].append('Additional unresolved-call notes omitted from this overview.')

            def visit(current_file, fn, depth, bindings):
                key = (current_file, fn['start'])
                if key in visited or depth > 3 or len(visited) >= 12:
                    note('Repeated/recursive helper or depth/function limit reached.')
                    return
                visited.add(key)
                current = modules[current_file]
                tokens, brackets = current['tokens'], current['pairs']
                context = {name: bindings.get(name) for name in fn['params']}
                for pos in range(fn['start'], fn['end'] - 1):
                    if tokens[pos].value == 'function' and tokens[pos + 1].kind == 'id':
                        context[tokens[pos + 1].value] = None
                j = fn['start']
                while j < fn['end']:
                    if tokens[j].kind == 'id' and j + 1 < fn['end'] and tokens[j + 1].value == '=' and (j == fn['start'] or tokens[j - 1].value not in ('const', 'let', 'var', '.', ':')):
                        context[tokens[j].value] = None
                    if tokens[j].value in ('const', 'let', 'var') and j + 2 < fn['end'] and tokens[j + 1].kind == 'id':
                        name, assign = tokens[j + 1].value, j + 2
                        while assign < fn['end'] and tokens[assign].value not in ('=', ';'):
                            assign += 1
                        context[name] = expression(current_file, assign + 1, context)[0] if assign < fn['end'] and tokens[assign].value == '=' else None
                    # Don't scan nested callback/function bodies as if they were executed.
                    nested = function_at(current, j, fn['end'], 'nested') if tokens[j].value in ('function', 'async', '(') else None
                    if nested:
                        note('Nested callback/function body was not expanded.')
                        j = nested['end'] + 1
                        continue
                    if tokens[j].kind != 'id' or (j > fn['start'] and tokens[j - 1].value in ('.', 'new')):
                        j += 1
                        continue
                    value = lookup(current_file, tokens[j].value, context)
                    k = j + 1
                    while k + 1 < fn['end'] and tokens[k].value == '.':
                        value = value + '.' + tokens[k + 1].value if isinstance(value, str) else None
                        k += 2
                    if k >= fn['end'] or tokens[k].value != '(' or k not in brackets:
                        j += 1
                        continue
                    args = arguments(current, k)
                    if value == 'response.status':
                        close = brackets[k]
                        if close + 3 < fn['end'] and tokens[close + 1].value == '.' and tokens[close + 2].value in ('json', 'send') and tokens[close + 3].value == '(':
                            value = 'response.' + tokens[close + 2].value
                            k = close + 3
                            args = arguments(current, k)
                    def operation(text):
                        if len(trace['operations']) >= 40:
                            return
                        idx = emit('handler_operation', text, current_file, tokens[j].line)
                        trace['operations'].append({'description': text, 'evidence_index': idx, 'owner': {'file': current_file, 'function': fn['name']}})
                        trace['evidence_indices'].append(idx)
                    if isinstance(value, tuple) and value[0] == 'function' and len(trace['evidence_indices']) < 60:
                        helper = modules[value[1]]['functions'][value[2]][0]
                        idx = emit('handler_call', fn['name'] + ' → ' + helper['name'], current_file, tokens[j].line, target={'file': value[1], 'function': helper['name']})
                        trace['evidence_indices'].append(idx)
                        passed = {name: expression(current_file, a, context)[0] for name, (a, b) in zip(helper['params'], args)}
                        visit(value[1], helper, depth + 1, passed)
                    elif value in ('pg-client.query', 'mysql-client.query', 'mysql-client.execute'):
                        if args and args[0][1] == args[0][0] + 1 and tokens[args[0][0]].kind == 'string':
                            sql = tokens[args[0][0]].value
                            clean = re.sub(r"'(?:''|[^'])*'", "''", sql)
                            clean = re.sub(r'/\*.*?\*/|--[^\n]*', ' ', clean, flags=re.S)
                            command = re.match(r'\s*(SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM)\b', clean, re.I) if ';' not in clean.strip().rstrip(';') else None
                            table = re.search(r'\b(?:FROM|INTO|UPDATE)\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)?)', clean, re.I)
                            if command and table:
                                verb = {'SELECT': 'Reads', 'INSERT': 'Adds', 'UPDATE': 'Updates', 'DELETE': 'Deletes'}[command.group(1).upper().split()[0]]
                                engine = 'PostgreSQL' if value.startswith('pg-') else 'MySQL'
                                operation(f'{verb} records in “{table.group(1)}” via {engine}.')
                            else:
                                note('SQL expression/table or multiple statements were not interpreted.')
                        else:
                            note('Dynamic SQL or query configuration object was not interpreted.')
                    elif value in ('response.json', 'response.send'):
                        fields = []
                        if args and tokens[args[0][0]].value == '{':
                            start = args[0][0]
                            for pos in range(start + 1, brackets.get(start, start)):
                                if current['depth'][pos] == current['depth'][start] + 1 and pos + 1 < len(tokens) and tokens[pos + 1].value == ':' and tokens[pos].kind in ('id', 'string'):
                                    fields.append(tokens[pos].value)
                        operation('Sends a response with fields: ' + ', '.join(fields[:12]) + '.' if fields else 'Sends a response; its contents were not established.')
                    elif value not in ('response.status',):
                        note(f'Call at {current_file}:{tokens[j].line} was not resolved to a supported operation.')
                    j += 1
                if len(trace['operations']) >= 40:
                    note('Operation output capped at 40.')

            initial = {name: 'response' if index == 1 else None for index, name in enumerate(function['params'])}
            visit(owner_file, function, 0, initial)
            trace['unknowns'] += ['JS/TS uses a bounded token recognizer, not a complete language parser. Only supported Express registration, named helpers and pg/mysql2 SQL patterns are traced.',
                                  'Middleware, router mount prefixes, callbacks, type semantics, branch outcomes, permissions, transaction success and runtime behavior are unverified.']
            trace['unknowns'] = list(dict.fromkeys(trace['unknowns']))[:30]
            report['route_traces'].append(trace)


def arguments_like_braces(module, start):
    # Named ES imports use the same balanced comma separation as call arguments.
    return arguments(module, start)
