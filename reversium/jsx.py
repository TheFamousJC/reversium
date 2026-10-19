"""Bounded JSX lexical adapter. Preserve expressions; discard markup text/attributes.

This is not a JSX/type parser. Tags are source references, never rendered UI proof.
"""
import re
import json


def jsx_tokens(source, tokenize):
    # This reader is entered only at an expression's opening JSX tag.
    tags, expressions = [], []

    def quoted(i):
        quote = source[i]
        i += 1
        while i < len(source):
            if source[i] == '\\':
                i += 2
            elif source[i] == quote:
                return i + 1
            else:
                i += 1
        raise ValueError('unterminated JSX attribute')

    def expression(i, component=None, prop=None):
        start, depth = i + 1, 1
        i += 1
        while i < len(source):
            if source[i] in "\"'`":
                i = quoted(i)
                continue
            if source.startswith('//', i):
                end = source.find('\n', i)
                i = len(source) if end < 0 else end
                continue
            if source.startswith('/*', i):
                end = source.find('*/', i + 2)
                if end < 0:
                    raise ValueError('unterminated JSX comment')
                i = end + 2
                continue
            depth += (source[i] == '{') - (source[i] == '}')
            if depth == 0:
                expressions.append((start, i, component, prop))
                return i + 1
            i += 1
        raise ValueError('unclosed JSX expression')

    i, stack = 0, []
    while i < len(source):
        if source[i] == '<':
            closing = source.startswith('</', i)
            match = re.match(r'</?([A-Za-z_$][\w$.-]*)?', source[i:])
            if not match:
                raise ValueError('unsupported JSX tag')
            name = match.group(1) or ''
            if not closing and name and name[0].isupper():
                tags.append((name, source[:i].count('\n')))
            i += len(match.group())
            while i < len(source) and source[i] != '>':
                if source[i] in "\"'":
                    i = quoted(i)
                elif source[i] == '{':
                    attribute = re.search(r'([A-Za-z_$][\w$-]*)\s*=\s*$', source[:i])
                    i = expression(i, name, attribute.group(1) if attribute else None)
                else:
                    i += 1
            if i >= len(source):
                raise ValueError('unclosed JSX tag')
            self_closing = i > 0 and source[i - 1] == '/'
            i += 1
            if closing:
                if not stack or stack.pop() != name:
                    raise ValueError('mismatched JSX tag')
            elif not self_closing:
                stack.append(name)
            if not stack:
                output = []
                from .js_tracing import Token
                output.extend(Token(name, 'jsx', offset + 1) for name, offset in tags)
                for start, end, component, prop in expressions:
                    offset = source[:start].count('\n')
                    if prop:
                        output.append(Token(json.dumps([component, prop]), 'jsx-prop', offset + 1))
                    bare = re.fullmatch(r'\s*([A-Za-z_$][\w$]*)\s*', source[start:end])
                    if bare:
                        output.append(Token(bare.group(1), 'jsx-ref', offset + 1))
                        continue
                    output.append(Token('(', 'punct', offset + 1))
                    output.extend(Token(t.value, t.kind, t.line + offset) for t in tokenize(source[start:end], jsx=True))
                    output.append(Token(')', 'punct', source[:end].count('\n') + 1))
                return output, i
        elif source[i] == '{':
            i = expression(i)
        else:
            # Raw JSX text (including apostrophes and code-looking text) is opaque.
            i += 1
    raise ValueError('unclosed JSX element')
