"""Bounded lexical prop/callback and API target tracing; never evaluates source."""
import json
import posixpath
import re
from dataclasses import dataclass
from .js_tracing import arguments


@dataclass
class Text:
    value: str
    evidence: tuple = ()


@dataclass
class Options:
    method: str | None
    evidence: tuple = ()
    specified: bool = False


@dataclass
class Undefined:
    pass


ENV_SCOPE = object()


class Workflows:
    def __init__(self, modules, node, link, enclosing, gaps):
        self.modules, self.node, self.link = modules, node, link
        self.enclosing, self.gaps = enclosing, gaps
        self.hooks, self.wrapped, self.lazy, self.props = {}, {}, {}, {}
        self.prop_calls, self.bindings, self.requests = 0, 0, []

    def owner(self, m, pos):
        fn = self.enclosing(m, pos)
        while fn and 'node' not in fn:
            fn = fn['parent']
        return fn['node'] if fn else m['node']

    def scopes(self, m, pos):
        fn = self.enclosing(m, pos)
        while fn:
            yield fn
            fn = fn['parent']
        yield None

    def variable(self, m, name, pos):
        for scope in self.scopes(m, pos):
            if scope and self.parameter(m, scope, name):
                return None
            values = [a for n, a, owner in m['variables'] if n == name and owner is scope]
            if values:
                if len(values) != 1:
                    return None
                a = values[0]
                if m.get('variable_kinds', {}).get(a) != 'const' or (name, id(scope)) in m['flow_reassigned']:
                    return None
                return a
        return None

    def parameter(self, m, fn, name):
        for a, b in arguments(m, fn['param']):
            if m['tokens'][a].value == name:
                return True
            if m['tokens'][a].value in ('{', '[') and any(t.kind == 'id' and t.value == name for t in m['tokens'][a:b]):
                return True  # Conservatively include destructured keys/aliases.
        return False

    def end(self, m, start):
        t, pairs, i = m['tokens'], m['pairs'], start
        while i < len(t) and t[i].value not in (';', ',', ')', '}', ']'):
            i = pairs.get(i, i) + 1
        return i

    def shadowed(self, m, name, pos):
        if name in m['imports']:
            return True
        for scope in self.scopes(m, pos):
            if (name, id(scope)) in m['flow_reassigned']:
                return True
            if scope and self.parameter(m, scope, name):
                return True
            if any(n == name and owner is scope for n, a, owner in m['variables']):
                return True
        return False

    def direct_callback(self, m, a, b):
        t, pairs = m['tokens'], m['pairs']
        for _ in range(6):
            if a < b and t[a].value == '(' and pairs.get(a) == b - 1:
                a, b = a + 1, b - 1
            else:
                break
        if a >= b:
            return None
        start = a + 1 if t[a].value == 'async' else a
        params = {start}
        if start < b and t[start].value == 'function':
            params = {start + 1, start + 2}
        return next((f for f in m['funcs'] if f['param'] in params and a <= f['param'] < b), None)

    def callable(self, m, name, pos, seen=()):
        key = (m['file'], name)
        if key in seen or len(seen) >= 8:
            return None
        seen += (key,)
        for scope in self.scopes(m, pos):
            if scope and self.parameter(m, scope, name):
                return None
            choices = [f for f in m['funcs'] if f['name'] == name and f['parent'] is scope and 'node' in f]
            if len(choices) == 1:
                return m, choices[0]
            if choices:
                return None
            wrapped = self.wrapped.get((m['file'], name, id(scope)))
            if wrapped:
                return m, wrapped
            local = [a for n, a, owner in m['variables'] if n == name and owner is scope]
            if local:
                a = self.variable(m, name, pos)
                if a is None:
                    return None
                lazy = self.lazy.get((m['file'], name))
                if lazy:
                    target, export = lazy
                    return self.callable(self.modules[target], export, len(self.modules[target]['tokens']), seen)
                if a + 1 < len(m['tokens']) and m['tokens'][a].kind == 'id' and m['tokens'][a + 1].value in (';', ','):
                    return self.callable(m, m['tokens'][a].value, a, seen)
                return None
        binding = m['imports'].get(name)
        if binding and binding[0] in self.modules:
            other = self.modules[binding[0]]
            if binding[1] == 'default':
                t = other['tokens']
                defaults = [t[i + 3].value for i in range(len(t) - 3) if [x.value for x in t[i:i + 3]] == ['export', 'default', 'function']]
                if len(defaults) != 1:
                    return None
                export = defaults[0]
            else:
                export = binding[1]
            return self.callable(other, export, len(other['tokens']), seen)
        return None

    def prop(self, m, name, pos, member=None):
        for fn in self.scopes(m, pos):
            if not fn:
                continue
            component = 'node' in fn and fn['name'][0].isupper() and m['file'].endswith(('.tsx', '.jsx'))
            if not component:
                if self.parameter(m, fn, name):
                    return None
                continue
            args = arguments(m, fn['param'])
            if not args:
                continue
            a, b = args[0]
            t = m['tokens']
            prop = None
            if member and t[a].value == name and t[a].kind == 'id':
                prop = member
            elif not member and t[a].value == '{' and a in m['pairs']:
                for x, y in arguments(m, a):
                    if any(t[k].value == '=' for k in range(x, y)):
                        continue  # Default expressions can replace the supplied value.
                    original = t[x].value
                    alias = t[x + 2].value if x + 2 < y and t[x + 1].value == ':' else original
                    if alias == name:
                        prop = original
            if prop:
                # A local declaration shadows the component parameter binding.
                if any(n == name and scope is not None and scope['start'] >= fn['start'] and start < pos
                       for n, start, scope in m['variables']):
                    return None
                return self.prop_node(m, fn, prop)
        return None

    def prop_node(self, m, fn, prop):
        key = (m['file'], fn['node'], prop)
        if key not in self.props:
            self.props[key] = self.node('helper', fn['name'] + '.prop:' + prop, key)
        return self.props[key]

    def reference(self, m, a, b):
        t = m['tokens']
        if b == a + 1 and t[a].kind in ('id', 'jsx-ref'):
            found = self.callable(m, t[a].value, a)
            return found[1]['node'] if found else self.prop(m, t[a].value, a)
        if b == a + 3 and t[a + 1].value in ('.', '?.'):
            prop = self.prop(m, t[a].value, a, t[a + 2].value)
            if prop:
                return prop
            init = self.variable(m, t[a].value, a)
            if init is not None and init + 1 < len(t) and t[init + 1].value == '(':
                hook = self.callable(m, t[init].value, init)
                if hook:
                    return self.hooks.get((hook[0]['file'], hook[1]['node'], t[a + 2].value))
        return None

    def prepare(self):
        for m in self.modules.values():
            t = m['tokens']
            m['flow_reassigned'] = {(t[i].value, id(self.enclosing(m, i))) for i in range(len(t) - 1)
                                    if t[i].kind == 'id' and t[i + 1].value == '='
                                    and not any(a == i + 2 for name, a, scope in m['variables'])
                                    and (i == 0 or t[i - 1].value not in ('.', ':'))}
        # Recognized React wrappers and lazy literal imports only.
        for m in self.modules.values():
            t, pairs = m['tokens'], m['pairs']
            for name, a, scope in m['variables']:
                wrapper = m['imports'].get(t[a].value)
                if not wrapper or wrapper[2] != 'react' or a + 1 not in pairs:
                    continue
                end = pairs[a + 1]
                if wrapper[1] == 'useCallback':
                    fns = [f for f in m['funcs'] if a + 1 < f['param'] < end and f['parent'] is scope]
                    if fns:
                        fn = min(fns, key=lambda f: f['param'])
                        fn['node'] = self.node('helper', (scope['name'] + '.' if scope else '') + name,
                                               (m['file'], scope['name'] if scope else '', name))
                        self.wrapped[(m['file'], name, id(scope))] = fn
                elif wrapper[1] == 'lazy':
                    imports = [k for k in range(a + 2, end - 2) if t[k].value == 'import' and t[k + 1].value == '(' and t[k + 2].kind == 'string']
                    if len(imports) != 1:
                        continue
                    k = imports[0]
                    package = t[k + 2].value
                    if not package.startswith('.'):
                        continue
                    base = posixpath.normpath(posixpath.join(posixpath.dirname(m['file']), package))
                    targets = [p for p in (base, base + '.tsx', base + '.ts', base + '.jsx', base + '.js', base + '/index.tsx') if p in self.modules]
                    exports = [t[q + 4].value for q in range(k + 3, end - 4) if t[q].value == 'default' and t[q + 1].value == ':' and t[q + 3].value == '.']
                    if len(targets) == 1 and len(exports) <= 1:
                        export = exports[0] if exports else None
                        if export is None:
                            target_tokens = self.modules[targets[0]]['tokens']
                            defaults = [target_tokens[q + 3].value for q in range(len(target_tokens) - 3) if [x.value for x in target_tokens[q:q + 3]] == ['export', 'default', 'function']]
                            if len(defaults) == 1:
                                export = defaults[0]
                        if export:
                            self.lazy[(m['file'], name)] = (targets[0], export)
        # Returned hook object callbacks, either return {...} or useMemo(()=>({...})).
        for m in self.modules.values():
            t, pairs = m['tokens'], m['pairs']
            for hook in m['funcs']:
                if 'node' not in hook or not hook['name'].startswith('use'):
                    continue
                objects = []
                for i in range(hook['start'], hook['end'] - 1):
                    if t[i].value != 'return' or self.enclosing(m, i) is not hook:
                        continue
                    a = i + 1
                    if t[a].value == '{':
                        objects.append(a)
                    elif m['imports'].get(t[a].value, (None, None, None))[1:] == ('useMemo', 'react') and a + 1 in pairs:
                        call_end = pairs[a + 1]
                        objects.extend(k for k in range(a + 2, call_end - 1) if t[k].value == '{' and k > 0 and t[k - 1].value == '(' and k > 1 and t[k - 2].value == '=>')
                for obj in objects:
                    if obj not in pairs:
                        continue
                    for a, b in arguments(m, obj):
                        if b == a + 1 and t[a].kind == 'id':
                            ref = self.reference(m, a, b)
                            if ref:
                                self.hooks[(m['file'], hook['node'], t[a].value)] = ref
                            continue
                        if a + 2 >= b or t[a].kind != 'id' or t[a + 1].value != ':':
                            continue
                        fn = self.direct_callback(m, a + 2, b)
                        if fn:
                            fn['node'] = self.node('helper', hook['name'] + '.return:' + t[a].value,
                                                   (m['file'], hook['node'], 'return', t[a].value))
                            self.hooks[(m['file'], hook['node'], t[a].value)] = fn['node']
                        else:
                            ref = self.reference(m, a + 2, b)
                            if ref:
                                self.hooks[(m['file'], hook['node'], t[a].value)] = ref

        # Inline JSX callbacks need nodes before the main reader scans their calls.
        for m in self.modules.values():
            t = m['tokens']
            serial = {}
            for i, token in enumerate(t):
                if token.kind != 'jsx-prop' or i + 1 not in m['pairs']:
                    continue
                component, prop = json.loads(token.value)
                a, b = i + 2, m['pairs'][i + 1]
                fn = self.direct_callback(m, a, b)
                if fn:
                    owner = self.owner(m, i)
                    key = (owner, component, prop)
                    serial[key] = serial.get(key, 0) + 1
                    fn['node'] = self.node('helper', component + '.' + prop + ' callback',
                                           (m['file'], key, serial[key]))

    def connect_props(self):
        for m in self.modules.values():
            t, pairs = m['tokens'], m['pairs']
            for i, token in enumerate(t):
                if token.kind == 'jsx-prop':
                    component, prop = json.loads(token.value)
                    if i + 1 >= len(t):
                        continue
                    if t[i + 1].kind == 'jsx-ref':
                        a, b = i + 1, i + 2
                    elif i + 1 in pairs:
                        a, b = i + 2, pairs[i + 1]
                    else:
                        continue
                    value = self.reference(m, a, b)
                    if not value:
                        fn = self.direct_callback(m, a, b)
                        value = fn.get('node') if fn else None
                    target = self.callable(m, component, i)
                    if value and target:
                        receiver = self.prop_node(target[0], target[1], prop)
                        self.link(receiver, value, 'prop binding candidate', m['file'], token.line, 'inferred')
                        self.bindings += 1
                        self.link(self.owner(m, i), target[0]['node'], 'component binding reference', m['file'], token.line)
                    elif value and component and component[0].islower():
                        self.link(self.owner(m, i), value, 'DOM event/value reference', m['file'], token.line)
                    elif prop.startswith('on') and component and component[0].isupper():
                        self.gaps.append(f'{m["file"]}:{token.line}: JSX callback binding for {component}.{prop} is unresolved.')
                if token.kind != 'id' or i and t[i - 1].value in ('.', '?.'):
                    continue
                j = i + 1
                if j + 1 < len(t) and t[j].value in ('.', '?.') and t[j + 1].kind == 'id':
                    j += 2
                if j < len(t) and t[j].value == '?.':
                    j += 1
                if j < len(t) and t[j].value == '(':
                    if any(fn['param'] == j for fn in m['funcs']):
                        continue
                    target = self.reference(m, i, j - 1 if t[j - 1].value == '?.' else j)
                    if target:
                        # Ordinary direct helper calls are already recorded by the
                        # structural reader; add only newly resolved bindings.
                        is_prop = target in self.props.values()
                        is_member = j > i + 1 and t[i + 1].value in ('.', '?.') and i + 2 < j and t[i + 2].kind == 'id'
                        wrapped = any(fn['node'] == target for fn in self.wrapped.values())
                        if not (is_prop or is_member or wrapped):
                            continue
                        label = 'invokes prop candidate' if is_prop else 'hook callback candidate' if is_member else 'call reference'
                        self.link(self.owner(m, i), target, label, m['file'], token.line, 'inferred')
                        self.prop_calls += 1

    def evaluate(self, m, a, b, env=None, seen=()):
        env = env or {}
        t, pairs = m['tokens'], m['pairs']
        if a >= b or len(seen) >= 10:
            return None
        evidence = ((m['file'], t[a].line),)
        if t[a].value == '(' and pairs.get(a) == b - 1:
            return self.evaluate(m, a + 1, b - 1, env, seen)
        if b == a + 1:
            token = t[a]
            if token.kind == 'string':
                return Text(token.value, evidence) if len(token.value) <= 2000 else None
            if token.kind == 'dynamic':
                if len(token.value) > 2000:
                    return None
                text = token.value.split('?', 1)[0].split('#', 1)[0]
                def substitute(match):
                    expression = match.group(1).strip()
                    if re.fullmatch(r'encodeURIComponent\([^()]+\)', expression) and not self.shadowed(m, 'encodeURIComponent', a):
                        return '{*}'
                    if re.fullmatch(r'[A-Za-z_$][\w$]*', expression):
                        value = self.evaluate_name(m, expression, a, env, seen)
                        if isinstance(value, Text) and '${' not in value.value:
                            return value.value
                    raise ValueError('unsupported interpolation')
                try:
                    value = re.sub(r'\$\{([^{}]*)\}', substitute, text)
                    return Text(value, evidence) if '${' not in value else None
                except ValueError:
                    return None
            if token.kind == 'id':
                if token.value == 'undefined':
                    return Undefined()
                return self.evaluate_name(m, token.value, a, env, seen)
        # Concatenation only; arbitrary operators/functions remain unknown.
        parts, current, i = [], a, a
        while i < b:
            if t[i].value == '+':
                parts.append((current, i)); current = i + 1
            i = pairs.get(i, i) + 1
        if parts:
            values = []
            for x, y in parts + [(current, b)]:
                value = self.evaluate(m, x, y, env, seen)
                values.append(value)
                if isinstance(value, Text) and ('?' in value.value or '#' in value.value) and all(isinstance(v, Text) for v in values):
                    return Text(''.join(v.value for v in values).split('?')[0].split('#')[0], tuple(e for v in values for e in v.evidence))
            if all(isinstance(v, Text) for v in values):
                text = ''.join(v.value for v in values)
                if len(text) <= 2000:
                    return Text(text, tuple(e for v in values for e in v.evidence))
        if t[a].value == 'encodeURIComponent' and a + 1 in pairs and pairs[a + 1] == b - 1 and not self.shadowed(m, 'encodeURIComponent', a):
            return Text('{*}', evidence)
        if t[a].value == '{' and pairs.get(a) == b - 1:
            method, known, locations, specified = 'GET', True, list(evidence), False
            for x, y in arguments(m, a):
                if x + 3 < y and [z.value for z in t[x:x + 3]] == ['.', '.', '.']:
                    spread = self.evaluate(m, x + 3, y, env, seen)
                    if isinstance(spread, Undefined):
                        continue
                    if isinstance(spread, Options):
                        if spread.specified:
                            method, known, specified = spread.method, spread.method is not None, True
                    else:
                        method, known, specified = None, False, True
                    if isinstance(spread, Options):
                        locations.extend(spread.evidence)
                elif x + 2 < y and t[x].value == 'method' and t[x + 1].value == ':':
                    value = self.evaluate(m, x + 2, y, env, seen)
                    known = isinstance(value, Text)
                    method = value.value.upper() if known else None
                    specified = True
            return Options(method if known else None, tuple(locations), specified)
        return None

    def evaluate_name(self, m, name, pos, env, seen):
        if name in env:
            for scope in self.scopes(m, pos):
                if scope is env.get(ENV_SCOPE):
                    return env[name]
                if scope and self.parameter(m, scope, name) or any(n == name and owner is scope for n, a, owner in m['variables']):
                    break
        key = (m['file'], name, pos)
        if key in seen:
            return None
        a = self.variable(m, name, pos)
        if a is not None:
            return self.evaluate(m, a, self.end(m, a), env, seen + (key,))
        return None

    def api_requests(self):
        # Follow helper call arguments separately at each call site; do not merge
        # all wrapper arguments into one global parameter value.
        calls, fetches = {}, {}
        for m in self.modules.values():
            t, pairs = m['tokens'], m['pairs']
            for i, token in enumerate(t[:-1]):
                if token.kind != 'id' or t[i + 1].value != '(' or i + 1 not in pairs or i and t[i - 1].value in ('.', '?.', 'function'):
                    continue
                if any(f['param'] == i + 1 for f in m['funcs']):
                    continue
                owner = self.owner(m, i)
                if token.value == 'fetch':
                    if self.shadowed(m, 'fetch', i):
                        self.gaps.append(f'{m["file"]}:{token.line}: shadowed fetch is not treated as an HTTP operation.')
                        continue
                    fetches.setdefault(owner, []).append((m, i, arguments(m, i + 1)))
                else:
                    target = self.callable(m, token.value, i)
                    if target:
                        calls.setdefault(owner, []).append((m, i, target, arguments(m, i + 1)))
        carriers = set(fetches)
        for _ in range(4):
            carriers.update(owner for owner, entries in calls.items() if any(target[1]['node'] in carriers for m, i, target, args in entries))
        resolved_fetches, walks = set(), 0
        def walk(owner, env, caller, evidence, depth=0, seen=()):
            nonlocal walks
            if depth > 4 or owner in seen or len(self.requests) >= 400 or walks >= 5000:
                return
            walks += 1
            for m, i, args in fetches.get(owner, []):
                if len(self.requests) >= 400:
                    return
                if not args:
                    continue
                value = self.evaluate(m, *args[0], env)
                if not isinstance(value, Text):
                    continue
                options = self.evaluate(m, *args[1], env) if len(args) > 1 else Options('GET')
                method = options.method if isinstance(options, Options) else None
                evidence_all = tuple(dict.fromkeys(evidence + value.evidence + ((m['file'], m['tokens'][i].line),) + (options.evidence if isinstance(options, Options) else ())))
                self.requests.append({'caller': caller, 'target': value.value, 'method': method, 'evidence': evidence_all})
                resolved_fetches.add((m['file'], i))
            for m, i, (cm, fn), args in calls.get(owner, []):
                if fn['node'] not in carriers:
                    continue
                params = arguments(cm, fn['param'])
                passed = {}
                for index, (a, b) in enumerate(params):
                    optional = a + 1 < b and cm['tokens'][a + 1].value == '?'
                    passed[cm['tokens'][a].value] = self.evaluate(m, *args[index], env) if index < len(args) else Undefined() if optional else None
                passed[ENV_SCOPE] = fn
                walk(fn['node'], passed, caller, evidence + ((m['file'], m['tokens'][i].line),), depth + 1, seen + (owner,))
        for owner in sorted(carriers):
            walk(owner, {}, owner, ())
        for entries in fetches.values():
            for m, i, args in entries:
                if (m['file'], i) not in resolved_fetches:
                    self.gaps.append(f'{m["file"]}:{m["tokens"][i].line}: API target remains unresolved by bounded constant/argument tracing.')
        if len(self.requests) >= 400:
            self.gaps.append('Computed API target output capped at 400 requests; helper propagation depth is 4.')
        if walks >= 5000:
            self.gaps.append('Computed API traversal capped at 5,000 helper contexts; unresolved calls remain unknown.')
        return self.requests
