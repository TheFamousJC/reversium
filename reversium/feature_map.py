"""Evidence-backed feature catalogue and interaction graph, no runtime inference."""
import hashlib
import html
import re


def stable_id(kind, *parts):
    return kind + '-' + hashlib.sha256('\0'.join(str(p) for p in parts).encode()).hexdigest()[:16]


def build_feature_map(report):
    nodes, edges, catalogue = {}, {}, []
    findings = report['findings']

    def node(kind, label, key, evidence, feature, unknowns=()):
        identity = stable_id(kind, key)
        entry = nodes.setdefault(identity, {'id': identity, 'kind': kind, 'label': label, 'evidence_indices': [], 'features': [], 'unknowns': list(unknowns)})
        entry['evidence_indices'] = sorted(set(entry['evidence_indices'] + list(evidence)))
        entry['features'] = sorted(set(entry['features'] + [feature]))
        return identity

    def edge(source, target, label, confidence, evidence, feature):
        identity = stable_id('edge', source, target, label)
        entry = edges.setdefault(identity, {'id': identity, 'source': source, 'target': target, 'label': label, 'confidence': confidence, 'evidence_indices': [], 'features': []})
        entry['evidence_indices'] = sorted(set(entry['evidence_indices'] + list(evidence)))
        entry['features'] = sorted(set(entry['features'] + [feature]))

    for trace in report.get('route_traces', [])[:100]:
        if not any('via PostgreSQL.' in op['description'] or 'via MySQL.' in op['description'] for op in trace['operations']) and any(root['file'] == trace.get('handler_file') and root.get('registered_path') == trace['route']
               for root in report.get('workspace_graph', {}).get('roots', [])):
            continue
        indices = trace['evidence_indices']
        if not indices:
            continue
        file = trace.get('handler_file', findings[indices[0]]['evidence']['file'])
        feature = stable_id('feature', file, trace['method'], trace['route'], trace['handler'])
        label = trace['method'] + ' ' + trace['route']
        node('feature', label, (file, label, trace['handler']), indices[:1], feature, trace['unknowns'])
        # Feature and node identities deliberately use the same canonical parts.
        feature_node = stable_id('feature', (file, label, trace['handler']))
        handler = node('handler', trace['handler'], (file, trace['handler']), indices[:1], feature)
        edge(feature_node, handler, 'handled by', 'traced', indices[:1], feature)
        operations = [operation['description'] for operation in trace['operations']]
        data_operations = [re.match(r'(Reads|Adds|Updates|Deletes) records in “([^”]+)”', text) for text in operations]
        data_operations = [match.groups() for match in data_operations if match]
        title = label
        if data_operations and len({table for _, table in data_operations}) == 1:
            actions = list(dict.fromkeys({'Reads': 'Read', 'Adds': 'Add', 'Updates': 'Update', 'Deletes': 'Delete'}[verb] for verb, _ in data_operations))
            title = ' / '.join(actions) + ' ' + data_operations[0][1] + ' records'
        catalogue.append({'id': feature, 'node_id': feature_node, 'name': label, 'handler': trace['handler'], 'file': file,
                          'title': title, 'description': ' '.join(dict.fromkeys(operations)) or 'Handler identified; no supported data/response operation traced.',
                          'evidence_indices': indices, 'unknowns': trace['unknowns'], 'confidence': 'static trace; not runtime verified'})
        for index in indices:
            finding = findings[index]
            target = finding.get('target')
            if finding['kind'] != 'handler_call' or not isinstance(target, dict):
                continue
            caller = finding['value'].split(' → ')[0]
            caller_file = finding['evidence']['file']
            caller_id = node('handler' if (caller_file, caller) == (file, trace['handler']) else 'helper', caller, (caller_file, caller), [index], feature)
            helper = node('helper', target['function'], (target['file'], target['function']), [index], feature)
            edge(caller_id, helper, 'calls', 'traced', [index], feature)
        for operation in trace['operations']:
            index = operation['evidence_index']
            description = operation['description']
            owner = operation.get('owner', {'file': file, 'function': trace['handler']})
            kind = 'handler' if (owner['file'], owner['function']) == (file, trace['handler']) else 'helper'
            owner_id = node(kind, owner['function'], (owner['file'], owner['function']), [index], feature)
            match = re.match(r'(Reads|Adds|Updates|Deletes) records in “([^”]+)” via (SQLite|PostgreSQL|MySQL)\.', description)
            if match:
                verb, table, engine = match.groups()
                resource = node('data', f'{engine}: {table}', (engine, table), [index], feature,
                                ['Shared table-name candidate only. Database identity, schema and runtime use are unverified; same names may refer to different databases.'])
                edge(owner_id, resource, verb.lower(), 'inferred', [index], feature)
            host = re.match(r'References web host “([^”]+)” in an HTTP request\.', description)
            if host:
                external = node('external', host.group(1), host.group(1), [index], feature,
                                ['Code reference only; successful communication and exchanged data are unverified.'])
                edge(owner_id, external, 'HTTP reference', 'traced', [index], feature)
        # Unresolved calls belong to this feature; they are gaps, not invented connections.
    workspace = report.get('workspace_graph', {})
    workspace_nodes = {n['id']: n for n in workspace.get('nodes', [])}
    outgoing = {}
    for item in workspace.get('edges', []):
        outgoing.setdefault(item['source'], []).append(item)
    for root in workspace.get('roots', []):
        feature = stable_id('workspace-feature', root['node'])
        pending, visited, indices, descriptions = [(root['node'], 0)], set(), set(root['evidence_indices']), []
        while pending and len(visited) < 240:
            identity, depth = pending.pop(0)
            if identity in visited or identity not in workspace_nodes:
                continue
            visited.add(identity)
            item = workspace_nodes[identity]
            entry = nodes.setdefault(identity, dict(item, features=[]))
            entry['features'] = sorted(set(entry['features'] + [feature]))
            for connection in outgoing.get(identity, []):
                # Imports are inventory references, not proof every imported function
                # participates in a feature. Follow explicit call/JSX/API references.
                if connection['label'] == 'imports' or depth >= 6:
                    continue
                target = workspace_nodes[connection['target']]
                child = nodes.setdefault(target['id'], dict(target, features=[]))
                child['features'] = sorted(set(child['features'] + [feature]))
                connection_entry = edges.setdefault(connection['id'], dict(connection, features=[]))
                connection_entry['features'] = sorted(set(connection_entry['features'] + [feature]))
                indices.update(connection['evidence_indices'])
                if target['kind'] in ('data', 'rpc', 'storage', 'auth', 'external'):
                    descriptions.append(connection['label'] + ': ' + target['label'])
                pending.append((target['id'], depth + 1))
        unknowns = ['Lexical references include conditional code and callback bodies; they do not prove execution or a user journey.',
                    'Supabase table/RPC/storage names are candidates; database identity, RPC effects, RLS, permissions and successful operations are unverified.',
                    'Router mount prefixes, middleware effects, dynamic targets, prop/event data flow, re-exports and runtime configuration remain unknown.']
        if pending:
            unknowns.append('Feature traversal capped at 240 nodes; full generated references are in workspace_graph JSON.')
        catalogue.append({'id': feature, 'node_id': root['node'], 'name': root['name'], 'title': root['name'], 'handler': root['name'], 'file': root['file'],
                          'description': '; '.join(dict.fromkeys(descriptions))[:2400] or 'Source references mapped; no supported data operation established.',
                          'evidence_indices': sorted(indices), 'unknowns': unknowns, 'confidence': 'static source references; not runtime verified', 'type': root['type']})
        nodes[root['node']]['unknowns'] = unknowns
    result = {'nodes': sorted(nodes.values(), key=lambda n: n['id']), 'edges': sorted(edges.values(), key=lambda e: e['id']),
              'features': catalogue, 'limits': 'Up to 100 traced features; graph view shows up to 120 nodes and 240 edges.',
              'coverage': {'route_candidates': sum(f['kind'] == 'route_candidate' for f in findings), 'traced_features': len(catalogue),
                           'route_references': sum(r['type'] == 'route' for r in workspace.get('roots', [])),
                           'react_modules': sum(r['type'] == 'react' for r in workspace.get('roots', [])), 'parsed_js_files': workspace.get('parsed_files', 0)},
              'unknowns': ['Edges show supported static paths, not proven execution or a complete call graph.',
                           'Shared data names indicate possible interaction, not a confirmed shared database or business workflow.',
                           'External dependencies are inventoried separately; unsupported external calls have no invented graph edges.']}
    return result


def compare_maps(current, previous):
    old_map = previous.get('feature_map')
    if not isinstance(old_map, dict):
        return {'status': 'unavailable', 'reason': 'Baseline has no feature interaction map; absence is not a removal.'}
    result = {'status': 'compared'}
    for key in ('features', 'nodes', 'edges'):
        before = {item['id']: item for item in old_map.get(key, [])}
        after = {item['id']: item for item in current.get('feature_map', {}).get(key, [])}
        result['added_' + key] = sorted(after.keys() - before.keys())
        result['removed_' + key] = sorted(before.keys() - after.keys())
        fields = ('name', 'description', 'unknowns') if key == 'features' else ('label', 'confidence', 'unknowns')
        def value(item, field):
            result = item.get(field)
            if field == 'unknowns' and isinstance(result, list):
                return [re.sub(r'(Call at .+:)\d+( was)', r'\1#\2', re.sub(r'Call on line \d+', 'Call on line #', text)) for text in result]
            return result
        result['changed_' + key] = sorted(identity for identity in after.keys() & before.keys() if any(value(after[identity], field) != value(before[identity], field) for field in fields))
        result['removed_' + key + '_details'] = [before[identity] for identity in result['removed_' + key]]
    old_nodes = {item['id']: item['label'] for item in old_map.get('nodes', [])}
    result['removed_connections'] = [{'source': old_nodes.get(item['source'], item['source']), 'target': old_nodes.get(item['target'], item['target']), 'label': item['label']} for item in result['removed_edges_details']]
    return result


def render_svg(graph, comparison=None):
    esc = lambda value: html.escape(str(value), quote=True)
    columns = {'feature': 0, 'module': 1, 'handler': 1, 'helper': 2, 'data': 3, 'external': 3, 'rpc': 3, 'storage': 3, 'auth': 3}
    feature_rank = {feature['id']: index for index, feature in enumerate(graph['features'])}
    chosen = sorted(graph['nodes'], key=lambda n: (columns[n['kind']], min((feature_rank.get(f, 999) for f in n['features']), default=999), n['label'], n['id']))[:120]
    added = set((comparison or {}).get('added_nodes', []))
    changed = set((comparison or {}).get('changed_nodes', []))
    changed_features = set((comparison or {}).get('changed_features', []))
    changed.update(feature['node_id'] for feature in graph['features'] if feature['id'] in changed_features)
    positions, counts = {}, [0] * 4
    for item in chosen:
        col = columns[item['kind']]
        positions[item['id']] = (25 + col * 310, 65 + counts[col] * 115)
        counts[col] += 1
    height = max(220, max(counts) * 115 + 90)
    output = [f'<svg id="feature-map-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1260 {height}" role="group" aria-label="Feature interaction map">',
              '<rect width="100%" height="100%" fill="#101823"/><defs><marker id="map-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="#9cafc8"/></marker></defs>']
    for col, title in enumerate(('Features', 'Handlers', 'Helpers', 'Data-name candidates')):
        output.append(f'<text x="{25+310*col}" y="28" fill="#afbdce" font-size="15">{title}</text>')
    drawn = 0
    for item in graph['edges']:
        if drawn >= 240 or item['source'] not in positions or item['target'] not in positions:
            continue
        drawn += 1
        x1, y1 = positions[item['source']]
        x2, y2 = positions[item['target']]
        x1 += 255
        y1 += 32
        y2 += 32
        dash = ' stroke-dasharray="7 5"' if item['confidence'] == 'inferred' else ''
        color = '#8fed75' if item['id'] in (comparison or {}).get('added_edges', []) else '#f8c86b' if item['id'] in (comparison or {}).get('changed_edges', []) else '#9cafc8'
        output.append(f'<g class="map-selectable" data-map-kind="edge" data-map-id="{item["id"]}" data-features="{esc(" ".join(item["features"]))}" role="button" tabindex="0" aria-label="Inspect connection: {esc(item["label"])} {item["id"]}"><title>{esc(item["label"])} ({item["confidence"]})</title><path d="M{x1} {y1} C{x1+45} {y1},{x2-45} {y2},{x2} {y2}" fill="none" stroke="{color}" stroke-width="2"{dash} marker-end="url(#map-arrow)"/><text x="{(x1+x2)//2}" y="{(y1+y2)//2-8}" fill="#b6c9de" style="font:11px system-ui" text-anchor="middle">{esc(item["label"])}</text></g>')
    for item in chosen:
        x, y = positions[item['id']]
        fill = '#253f44' if item['kind'] == 'data' else '#1c2838'
        stroke = '#8fed75' if item['id'] in added else '#f8c86b' if item['id'] in changed else '#66d9c2'
        label = item['label']
        output.append(f'<g class="map-selectable" data-map-kind="node" data-map-id="{item["id"]}" data-features="{esc(" ".join(item["features"]))}" role="button" tabindex="0" aria-label="Inspect {esc(item["kind"])}: {esc(label)}"><title>{esc(label)}</title><rect x="{x}" y="{y}" width="255" height="72" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"/><text x="{x+12}" y="{y+27}" fill="#e8edf5" font-size="14">{esc(label[:30])}</text><text x="{x+12}" y="{y+52}" fill="#afbdce" font-size="12">{esc(item["kind"])} · {len(item["features"])} feature(s)</text></g>')
    output.append('</svg>')
    return ''.join(output), {'omitted_nodes': len(graph['nodes']) - len(chosen), 'omitted_edges': len(graph['edges']) - drawn}
