import unittest
from reversium.analyze import inspect_zip
from test_reversium import archive

APP = '''import express from 'express';
import { Pool } from 'pg';
import { listContacts } from './storage';
const app = express();
const pool: Pool = new Pool();
app.get('/contacts', async (req: Request, res: Response) => {
  const rows = await listContacts(pool);
  res.json({contacts: rows});
});
'''
HELPER = '''export async function listContacts(db: Pool) {
  return await db.query('SELECT name FROM contacts');
}
'''


class JavaScriptTracingTests(unittest.TestCase):
    def test_typescript_cross_file_pg_and_response(self):
        report = inspect_zip(archive([('app.ts', APP), ('storage.ts', HELPER)]))
        self.assertEqual(len(report['route_traces']), 1)
        trace = report['route_traces'][0]
        self.assertIn('Reads records in “contacts” via PostgreSQL.', str(trace['operations']))
        self.assertIn('Sends a response with fields: contacts.', str(trace['operations']))
        evidence = [report['findings'][i]['evidence'] for i in trace['evidence_indices']]
        self.assertIn({'file': 'storage.ts', 'line': 2}, evidence)
        self.assertTrue(any(n['kind'] == 'data' for n in report['feature_map']['nodes']))

    def test_mysql_writes_and_no_values_in_trace(self):
        code = '''import express from 'express';
import mysql from 'mysql2/promise';
const app = express();
const db = mysql.createPool({password: 'PRIVATE_VALUE'});
app.post('/contacts', async (req, res) => {
  await db.execute("INSERT INTO contacts(name) VALUES ('PRIVATE_VALUE')");
  await db.query('UPDATE contacts SET active = 1');
  await db.query('DELETE FROM contacts');
  res.status(201).json({created: true});
});'''
        trace = inspect_zip(archive([('app.js', code)]))['route_traces'][0]
        self.assertIn('Adds records', str(trace['operations']))
        self.assertIn('Updates records', str(trace['operations']))
        self.assertIn('Deletes records', str(trace['operations']))
        self.assertIn('fields: created', str(trace['operations']))
        self.assertNotIn('PRIVATE_VALUE', str(trace))

    def test_comments_and_strings_do_not_create_supported_routes(self):
        code = '''import express from 'express'; const app = express();
// app.get('/fake', (req,res) => {res.json({fake: true});});
const text = "app.get('/also-fake', handler)";
'''
        self.assertEqual(inspect_zip(archive([('app.js', code)]))['route_traces'], [])

    def test_arbitrary_client_and_dynamic_sql_remain_unknown(self):
        code = '''import express from 'express'; import {Pool} from 'pg';
const app=express(); const db=new Pool();
app.post('/x', async (req,res)=> {const other = unknown(); other.query('DELETE FROM records'); db.query(req.body.sql);});'''
        trace = inspect_zip(archive([('app.js', code)]))['route_traces'][0]
        self.assertEqual(trace['operations'], [])
        self.assertTrue(any('Dynamic SQL' in note for note in trace['unknowns']))

    def test_nested_function_is_not_executed_and_parameter_shadows(self):
        code = '''import express from 'express';import {Pool} from 'pg';const app=express();const db=new Pool();
function helper(db) {db.query('DELETE FROM records');}
app.get('/x',(req,res)=> {function uncalled(){db.query('DELETE FROM secret_table');} helper(unknown);});'''
        trace = inspect_zip(archive([('app.js', code)]))['route_traces'][0]
        self.assertNotIn('Deletes records', str(trace['operations']))

    def test_unsupported_regex_and_malformed_syntax_are_reported(self):
        for code in ('const pattern = /app.get("fake")/;', 'function broken( {'):
            report = inspect_zip(archive([('app.js', code)]))
            self.assertEqual(report['route_traces'], [])
            self.assertTrue(any('tracing skipped' in note for note in report['warnings']))

    def test_nested_name_shadowing_does_not_call_global_helper(self):
        code = '''import express from 'express';import {Pool} from 'pg';const app=express();const db=new Pool();
function helper() {db.query('DELETE FROM records');}
app.get('/x',(req,res)=> {function helper(){return 1;} helper();});'''
        trace = inspect_zip(archive([('app.js', code)]))['route_traces'][0]
        self.assertNotIn('Deletes records', str(trace['operations']))
