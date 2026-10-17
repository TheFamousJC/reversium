"""Bounded, contiguous source paths for reading a graph one workflow at a time."""
from collections import deque


def workflow_paths(graph):
    nodes = {node['id']: node for node in graph.get('nodes', [])}
    outgoing = {}
    for edge in graph.get('edges', []):
        outgoing.setdefault(edge['source'], []).append(edge)
    paths = []
    for feature in graph.get('features', []):
        if feature.get('type') != 'react':
            continue
        root = feature['node_id']
        queue = deque([(root, [], frozenset([root]), False, False)])
        seen = set()
        examined = 0
        while queue and examined < 3000:
            identity, chain, visited, callback, api = queue.popleft()
            examined += 1
            state = (identity, callback, api)
            if state in seen:
                continue
            seen.add(state)
            if nodes[identity]['kind'] == 'data' and callback and api:
                paths.append({'screen': feature['name'], 'edges': chain,
                              'nodes': [nodes[root]] + [nodes[e['target']] for e in chain]})
                break  # One shortest supported data branch per screen, not all journeys.
            if len(chain) >= 12:
                continue
            for edge in sorted(outgoing.get(identity, []), key=lambda e: e['id']):
                target = edge['target']
                if target not in nodes or target in visited:
                    continue
                # Crossing a rendered child would attribute its actions to another screen.
                if edge['label'] in ('imports', 'JSX reference', 'component binding reference'):
                    continue
                if nodes[target]['kind'] == 'module':
                    continue
                is_callback = callback or edge['label'] in ('invokes prop candidate', 'prop binding candidate', 'DOM event/value reference', 'JSX value reference')
                if edge['label'].startswith('API target candidate ') and not callback:
                    continue
                is_api = api or edge['label'].startswith('API target candidate ')
                queue.append((target, chain + [edge], visited | {target}, is_callback, is_api))
    return sorted(paths, key=lambda path: (not any(e['label'] == 'invokes prop candidate' for e in path['edges']), path['screen']))
