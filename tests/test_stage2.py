import json
import unittest
from pathlib import Path
from reversium.analyze import inspect_zip
from reversium.report import render
from reversium.source import compare_reports
from test_reversium import archive


class SourceStageTests(unittest.TestCase):
    def fixture(self):
        root = Path(__file__).parent / 'fixtures' / 'webapp'
        return inspect_zip(archive([(p.relative_to(root).as_posix(), p.read_bytes()) for p in root.rglob('*') if p.is_file()]))

    def test_fixture_resolution_and_framework_candidates(self):
        report = self.fixture()
        imports = {f['value']: f for f in report['findings'] if f['kind'] == 'import'}
        self.assertEqual(imports['.models']['target'], 'backend/models.py')
        self.assertEqual(imports['./users.js']['target'], 'frontend/users.ts')
        self.assertEqual(imports['express']['resolution'], 'external')
        self.assertEqual(imports['missing_library']['resolution'], 'unresolved')
        self.assertEqual(imports['unknown-package']['resolution'], 'unresolved')
        route = next(f for f in report['findings'] if f['kind'] == 'route_candidate')
        self.assertEqual(route['value'], '/users')
        self.assertEqual(route['evidence']['line'], 6)
        self.assertTrue(any(f['kind'] == 'model_candidate' and f['value'] == 'User' for f in report['findings']))

    def test_manifest_coverage(self):
        report = self.fixture()
        deps = {f['value'] for f in report['findings'] if f['kind'] == 'dependency'}
        self.assertEqual(deps, {'express', 'Flask', 'SQLAlchemy', 'example.test/library'})
        self.assertEqual(report['coverage']['python_ast'], 2)

    def test_ambiguous_modules_not_chosen(self):
        report = inspect_zip(archive([('main.ts', 'import x from "./lib"'), ('lib.ts', ''), ('lib.js', '')]))
        finding = report['findings'][0]
        self.assertEqual(finding['resolution'], 'ambiguous')
        self.assertNotIn('target', finding)

    def test_archive_paths_normalized_and_duplicates_rejected(self):
        report = inspect_zip(archive([('./pkg/main.py', 'from . import helper'), ('pkg/helper.py', '')]))
        self.assertEqual(report['findings'][0]['target'], 'pkg/helper.py')
        with self.assertRaises(ValueError):
            inspect_zip(archive([('./main.py', ''), ('main.py', '')]))

    def test_invalid_relative_import_not_linked(self):
        report = inspect_zip(archive([('pkg/main.py', 'from ... import helper'), ('helper.py', '')]))
        self.assertEqual(report['findings'][0]['resolution'], 'unresolved')

    def test_comment_is_not_a_python_route(self):
        report = inspect_zip(archive([('main.py', '# @app.get("/fake")\ntext = "@app.get(\\"/also-fake\\")"')]))
        self.assertFalse(any(f['kind'] == 'route_candidate' for f in report['findings']))

    def test_compare_ignores_lines_and_tracks_changes(self):
        before = inspect_zip(archive([('a.py', 'import os'), ('removed.txt', '')]))
        after = inspect_zip(archive([('a.py', '\nimport os\nimport json'), ('added.txt', '')]))
        delta = compare_reports(after, before)
        self.assertEqual(delta['changed_source_files'], ['a.py'])
        self.assertEqual(delta['added_files'], ['added.txt'])
        self.assertEqual(delta['removed_files'], ['removed.txt'])
        self.assertEqual([f['value'] for f in delta['added_findings'] if f['kind'] != 'file_review_signal'], ['json'])
        self.assertEqual([(f['kind'], f['file']) for f in delta['removed_findings']], [('file_review_signal', 'removed.txt')])
        self.assertEqual([f['file'] for f in delta['added_findings'] if f['kind']=='file_review_signal'], ['added.txt'])
        with self.assertRaises(ValueError):
            compare_reports(after, {'schema_version': 99})

    def test_report_data_cannot_escape_script(self):
        report = inspect_zip(archive([('a.py', '')]))
        report['warnings'].append('</script><script>alert(1)</script>')
        output = render(report)
        self.assertNotIn('</script><script>alert(1)', output)
        payload = output.split('id="report-data">')[1].split('</script>')[0]
        self.assertEqual(json.loads(payload), report)
        self.assertIn('Download HTML', output)


if __name__ == '__main__':
    unittest.main()
