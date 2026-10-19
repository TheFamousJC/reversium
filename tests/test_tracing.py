import unittest
from test_reversium import archive
from reversium.analyze import inspect_zip
from reversium.sample import sample_archive
from reversium.__main__ import LocalHTTPServer, Handler


class HandlerTracingTests(unittest.TestCase):
    def test_live_server_cannot_share_an_occupied_port(self):
        server = LocalHTTPServer(('127.0.0.1', 0), Handler)
        try:
            with self.assertRaises(OSError):
                other = LocalHTTPServer(('127.0.0.1', server.server_port), Handler)
                other.server_close()
        finally:
            server.server_close()

    def test_sample_traces_cross_file_reads_writes_and_commit(self):
        report = inspect_zip(sample_archive())
        traces = report['route_traces']
        self.assertEqual(len(traces), 2)
        read = traces[0]
        self.assertTrue(any('Reads records in “contacts”' in op['description'] for op in read['operations']))
        self.assertTrue(any('Returns rows read' in op['description'] for op in read['operations']))
        write = traces[1]
        self.assertTrue(any('Adds records' in op['description'] for op in write['operations']))
        self.assertTrue(any('committed' in op['description'] for op in write['operations']))
        self.assertTrue(any('fields: created' in op['description'] for op in write['operations']))
        evidence = [report['findings'][i]['evidence'] for i in read['evidence_indices']]
        self.assertIn({'file': 'app.py', 'line': 7}, evidence)
        self.assertIn({'file': 'storage.py', 'line': 2}, evidence)
        self.assertTrue(any(e['topic'] == 'Feature traced through code' for e in report['behavior']['explanations']))

    def test_returns_do_not_disclose_values(self):
        report = inspect_zip(archive([('app.py', '@app.get("/health")\ndef health():\n    return {"ok": True, "token": "SECRET_VALUE"}')]))
        trace = report['route_traces'][0]
        self.assertIn('fields: ok, token', str(trace['operations']))
        self.assertNotIn('SECRET_VALUE', str(trace))

    def test_generic_execute_is_not_a_database(self):
        code = '@app.get("/x")\ndef action(client):\n    client.execute("DELETE FROM contacts")'
        trace = inspect_zip(archive([('app.py', code)]))['route_traces'][0]
        self.assertEqual(trace['operations'], [])
        self.assertTrue(any('not resolved' in u for u in trace['unknowns']))

    def test_select_literal_does_not_invent_a_table_read(self):
        code = '''import sqlite3
@app.get('/x')
def route():
    conn = sqlite3.connect('x')
    conn.execute("SELECT 'FROM hidden_table'")
'''
        trace = inspect_zip(archive([('app.py', code)]))['route_traces'][0]
        self.assertNotIn('Reads records', str(trace['operations']))
        self.assertNotIn('hidden_table', str(trace['operations']))
        self.assertIn('no table was identified', str(trace['operations']))

    def test_dynamic_sql_is_unknown_and_nested_function_not_run(self):
        code = '''import sqlite3
@app.get('/x')
def route(sql):
    conn = sqlite3.connect('x')
    conn.execute(sql)
    def never_called():
        return {'should_not_appear': True}
'''
        trace = inspect_zip(archive([('app.py', code)]))['route_traces'][0]
        self.assertTrue(any('Dynamic SQL' in u for u in trace['unknowns']))
        self.assertNotIn('should_not_appear', str(trace['operations']))

    def test_recursive_helper_bounded(self):
        code = 'def helper():\n    return helper()\n@app.get("/x")\ndef route():\n    return helper()'
        trace = inspect_zip(archive([('app.py', code)]))['route_traces'][0]
        self.assertTrue(any('recursive' in u for u in trace['unknowns']))

    def test_parameter_shadowing_does_not_follow_global_helper(self):
        code = 'def helper():\n    return {"not_called": True}\n@app.get("/x")\ndef route(helper):\n    return helper()'
        trace = inspect_zip(archive([('app.py', code)]))['route_traces'][0]
        self.assertEqual(trace['operations'], [])

    def test_cursor_update_delete_and_literal_sql_not_leaked(self):
        code = '''import sqlite3 as sql
@app.post('/x')
def route():
    conn = sql.connect('x')
    cursor = conn.cursor()
    cursor.execute("UPDATE contacts SET name = 'PRIVATE_VALUE'")
    cursor.execute("DELETE FROM contacts")
'''
        trace = inspect_zip(archive([('app.py', code)]))['route_traces'][0]
        self.assertIn('Updates records', str(trace['operations']))
        self.assertIn('Deletes records', str(trace['operations']))
        self.assertNotIn('PRIVATE_VALUE', str(trace))


if __name__ == '__main__':
    unittest.main()
