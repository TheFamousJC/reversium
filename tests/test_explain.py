import json
import unittest
from reversium.analyze import inspect_zip
from reversium.report import render
from test_reversium import archive
from binary_fixtures import pe_fixture


class ExplanationTests(unittest.TestCase):
    def test_every_explanation_has_existing_evidence(self):
        report = inspect_zip(archive([('app.py', 'from fastapi import FastAPI\n@app.get("/users")\ndef users(): pass'), ('requirements.txt', 'psycopg\nredis')]))
        behavior = report['behavior']
        self.assertTrue(behavior['explanations'])
        for item in behavior['explanations']:
            self.assertTrue(item['evidence_indices'])
            for index in item['evidence_indices']:
                self.assertTrue(0 <= index < len(report['findings']))
            self.assertTrue(item['unknown'])
            self.assertIn('not verified', item['assessment'])
        route = next(item for item in behavior['explanations'] if item['topic'] == 'Possible web entry point')
        evidence = report['findings'][route['evidence_indices'][0]]
        self.assertEqual(evidence['value'], '/users')
        self.assertEqual(evidence['evidence']['line'], 2)
        self.assertNotIn('manages users', route['explanation'])

    def test_no_evidence_means_unknown(self):
        behavior = inspect_zip(archive([('README.txt', 'An amazing accounting platform that does everything')]))['behavior']
        self.assertEqual(behavior['explanations'], [])
        self.assertIn('not enough supported evidence', behavior['summary'])
        self.assertTrue(behavior['unknowns'])

    def test_binary_strings_do_not_become_business_claims(self):
        report = inspect_zip(archive([('app.exe', pe_fixture() + b'\0Automatically transfers money\0')]))
        behavior = report['behavior']
        self.assertNotIn('transfers money', json.dumps(behavior))
        self.assertTrue(any(item['topic'] == 'Compiled component' for item in behavior['explanations']))
        self.assertTrue(any('Compiled code' in item for item in behavior['unknowns']))

    def test_service_use_is_not_confirmed(self):
        report = inspect_zip(archive([('requirements.txt', 'psycopg>=3')]))
        item = next(item for item in report['behavior']['explanations'] if item['topic'] == 'Possible supporting service')
        self.assertIn('may keep organized records', item['explanation'])
        self.assertIn('optional', item['unknown'])
        self.assertEqual(report['findings'][item['evidence_indices'][0]]['value'], 'psycopg')

    def test_explanation_limits_keep_full_findings(self):
        code = '\n'.join(f'@app.get("/route-{i}")\ndef route_{i}(): pass\n' for i in range(25))
        report = inspect_zip(archive([('routes.py', code)]))
        self.assertEqual(len(report['behavior']['explanations']), 16)
        self.assertEqual(report['behavior']['omitted_groups'], 9)
        self.assertEqual(sum(item['kind'] == 'route_candidate' for item in report['findings']), 25)

    def test_html_explanations_escape_names_and_link_findings(self):
        report = inspect_zip(archive([('app.py', '@app.get("/<script>")\ndef route(): pass')]))
        output = render(report)
        self.assertIn('What this software does', output)
        self.assertNotIn('“/<script>”', output)
        self.assertIn('“/&lt;script&gt;”', output)
        for item in report['behavior']['explanations']:
            for index in item['evidence_indices']:
                self.assertIn(f'href="#finding-{index}"', output)
                self.assertIn(f'id="finding-{index}"', output)
        payload = output.split('id="report-data">')[1].split('</script>')[0]
        self.assertEqual(json.loads(payload)['behavior'], report['behavior'])


if __name__ == '__main__':
    unittest.main()
