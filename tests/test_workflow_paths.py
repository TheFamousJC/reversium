import unittest
from reversium.workflow_paths import workflow_paths


class WorkflowPathsTests(unittest.TestCase):
    def graph(self):
        kinds = ['module', 'helper', 'helper', 'feature', 'handler', 'data']
        labels = ['JSX value reference', 'prop binding candidate', 'API target candidate POST', 'handler reference', 'adds']
        return {'nodes': [{'id': str(i), 'label': str(i), 'kind': kind, 'evidence_indices': [i]} for i, kind in enumerate(kinds)],
                'edges': [{'id': str(i), 'source': str(i), 'target': str(i+1), 'label': label, 'evidence_indices': [i], 'confidence': 'inferred'} for i, label in enumerate(labels)],
                'features': [{'node_id': '0', 'name': 'Screen', 'type': 'react'}]}

    def test_contiguous_path_preserves_edge_evidence(self):
        graph = self.graph()
        path, = workflow_paths(graph)
        self.assertEqual(path['edges'], graph['edges'])
        self.assertEqual(path['nodes'], graph['nodes'])

    def test_missing_api_or_callback_never_invents_path(self):
        for index in (0, 2):
            graph = self.graph()
            graph['edges'][index]['label'] = 'call reference'
            if index == 0:
                graph['edges'][1]['label'] = 'call reference'
            self.assertEqual(workflow_paths(graph), [])

    def test_imports_children_cycles_and_depth_are_bounded(self):
        for label in ('imports', 'JSX reference', 'component binding reference'):
            graph = self.graph()
            graph['edges'][0]['label'] = label
            self.assertEqual(workflow_paths(graph), [])
        graph = self.graph()
        graph['edges'].append(dict(graph['edges'][0], id='cycle', source='1', target='0'))
        self.assertEqual(len(workflow_paths(graph)), 1)
        for i in range(6, 20):
            graph['nodes'].append(dict(graph['nodes'][1], id=str(i)))
            graph['edges'].append(dict(graph['edges'][1], id=str(i), source=str(i), target=str(i+1)))
        graph['edges'][4]['target'] = '6'
        self.assertEqual(workflow_paths(graph), [])

    def test_deterministic_under_edge_order_changes(self):
        graph = self.graph()
        before = workflow_paths(graph)
        graph['edges'].reverse()
        self.assertEqual(before, workflow_paths(graph))
