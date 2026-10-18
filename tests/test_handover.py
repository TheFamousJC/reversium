import io,json,unittest,zipfile
from reversium.analyze import inspect_zip
from reversium.report import render


def scan(files):
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w') as z:
        for name,source in files.items():z.writestr(name,source)
    stream.seek(0);return inspect_zip(stream)


class HandoverTests(unittest.TestCase):
    def test_names_only_and_evidence_locations(self):
        report=scan({'.env.example':'DATABASE_URL=secret-value-never-export\nTOKEN=hidden-token\n','app.ts':"const x=process.env.DATABASE_URL; const y=import.meta.env.VITE_URL;\n",'app.py':"import os\nx=os.getenv('TOKEN')\ny=os.environ['DATABASE_URL']\n",'package.json':json.dumps({'scripts':{'start':'secret-command-never-export'},'engines':{'node':'>=20'}})})
        findings=report['findings'];encoded=json.dumps(report)
        self.assertNotIn('secret-value-never-export',encoded);self.assertNotIn('hidden-token',encoded);self.assertNotIn('secret-command-never-export',encoded)
        self.assertTrue(any(f['kind']=='project_script_name' and f['value']=='start' for f in findings))
        self.assertTrue(any(f['kind']=='runtime_constraint_candidate' and f['value']=='node: >=20' for f in findings))
        clue=next(c for c in report['handover']['clues'] if c['name']=='DATABASE_URL')
        self.assertTrue(clue['template_name_found']);self.assertTrue(all(i<len(findings) for i in clue['evidence_indices']))
        self.assertIn({'file':'app.py','line':3},[findings[i]['evidence'] for i in clue['evidence_indices']])

    def test_real_env_file_not_read_and_no_missing_requirement_claim(self):
        report=scan({'.env':'PASSWORD=private-value','app.ts':'const key=process.env.MAYBE_OPTIONAL;'})
        self.assertNotIn('private-value',json.dumps(report));self.assertFalse(report['handover']['clues'][0]['template_name_found'])
        html=render(report)
        self.assertIn('Required value/setup unconfirmed',html);self.assertIn('Reviewer statuses are your annotations',html)

    def test_empty_and_malformed_manifest_are_safe(self):
        report=scan({'package.json':'broken'})
        self.assertEqual(report['handover']['clues'],[]);self.assertEqual(len(report['handover']['tasks']),5)
        self.assertIn('id="tab-impact"',render(report));self.assertIn('id="tab-handover"',render(report))

    def test_malicious_script_names_are_not_interpreted(self):
        report=scan({'package.json':json.dumps({'scripts':{'<script>':'do not run','build':'not executed'},'engines':{'node':'secret-value'}})})
        self.assertEqual([c['name'] for c in report['handover']['clues']],['build'])

    def test_graph_records_source_files_for_impact_seeds(self):
        report=scan({'src/app.ts':"import express from 'express'; const app=express(); app.get('/hello', (req,res)=>{res.json({ok:true});});"})
        nodes=[n for n in report['feature_map']['nodes'] if n['kind'] in {'module','helper','handler','feature'}]
        self.assertTrue(nodes);self.assertTrue(all(n.get('file')=='src/app.ts' for n in nodes))

    def test_exact_archive_identity_includes_unread_content(self):
        a=scan({'.env':'private-one'});b=scan({'.env':'private-two'})
        self.assertEqual(len(a['archive_sha256']),64)
        self.assertNotEqual(a['archive_sha256'],b['archive_sha256'])
        self.assertIn('id="baseline-import"',render(a))
        self.assertIn('id="handover-import"',render(a))
