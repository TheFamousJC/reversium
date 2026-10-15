import unittest
import xml.etree.ElementTree as ET
from reversium.analyze import inspect_zip
from reversium.sample import sample_archive
from reversium.feature_map import render_svg, compare_maps
from test_reversium import archive


class FeatureMapTests(unittest.TestCase):
    def test_shared_data_has_two_features_and_inferred_edges(self):
        report = inspect_zip(sample_archive())
        graph = report['feature_map']
        self.assertEqual(len(graph['features']), 2)
        data = next(n for n in graph['nodes'] if n['kind'] == 'data')
        self.assertEqual(len(data['features']), 2)
        edges = [e for e in graph['edges'] if e['target'] == data['id']]
        self.assertEqual({e['label'] for e in edges}, {'reads', 'adds'})
        self.assertTrue(all(e['confidence'] == 'inferred' for e in edges))
        self.assertIn('Database identity', data['unknowns'][0])
        ids = {n['id'] for n in graph['nodes']}
        for edge in graph['edges']:
            self.assertIn(edge['source'], ids)
            self.assertIn(edge['target'], ids)
            self.assertTrue(edge['evidence_indices'])
            for index in edge['evidence_indices']:
                self.assertLess(index, len(report['findings']))

    def test_map_comparison_ignores_line_movement(self):
        before = inspect_zip(archive([('app.py', '@app.get("/x")\ndef x():\n    return {"ok": True}')]))
        after = inspect_zip(archive([('app.py', '\n\n@app.get("/x")\ndef x():\n    return {"ok": True}')]))
        comparison = compare_maps(after, before)
        self.assertEqual(comparison['added_features'], [])
        self.assertEqual(comparison['removed_edges'], [])
        self.assertEqual(comparison['changed_features'], [])
        self.assertEqual(compare_maps(after, {})['status'], 'unavailable')

    def test_added_feature_detected(self):
        before = inspect_zip(archive([('app.py', '@app.get("/x")\ndef x(): return []')]))
        after = inspect_zip(archive([('app.py', '@app.get("/x")\ndef x(): return []\n@app.post("/x")\ndef create(): return {}')]))
        self.assertEqual(len(compare_maps(after, before)['added_features']), 1)
        delta = compare_maps(after, before)
        self.assertIn('#8fed75', render_svg(after['feature_map'], delta)[0])
        reverse = compare_maps(before, after)
        self.assertTrue(reverse['removed_connections'])

    def test_svg_is_standalone_and_escapes_labels(self):
        graph = inspect_zip(archive([('app.py', '@app.get("/<script>")\ndef x(): return {}')]))['feature_map']
        svg, omissions = render_svg(graph)
        ET.fromstring(svg)
        self.assertNotIn('/<script>', svg)
        self.assertEqual(omissions['omitted_nodes'], 0)

    def test_changed_feature_highlight(self):
        before = inspect_zip(archive([('app.py', '@app.get("/x")\ndef x(): return {"old": True}')]))
        after = inspect_zip(archive([('app.py', '@app.get("/x")\ndef x(): return {"new": True}')]))
        delta = compare_maps(after, before)
        self.assertEqual(len(delta['changed_features']), 1)
        self.assertIn('#f8c86b', render_svg(after['feature_map'], delta)[0])

    def test_dependency_alone_does_not_become_an_interaction(self):
        report = inspect_zip(archive([('requirements.txt', 'redis\npsycopg')]))
        self.assertEqual(report['feature_map']['edges'], [])

    def test_http_reference_has_evidence_and_no_credentials(self):
        report = inspect_zip(archive([('app.py', 'import requests\n@app.get("/sync")\ndef sync():\n    return requests.get("https://user:secret@api.example.test/private?token=x")')]))
        external = next(n for n in report['feature_map']['nodes'] if n['kind'] == 'external')
        self.assertEqual(external['label'], 'https://api.example.test')
        self.assertNotIn('secret', str(report['feature_map']))
