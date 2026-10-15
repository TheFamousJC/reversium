import io
import http.client
import json
import stat
import threading
import unittest
import urllib.request
import urllib.error
import warnings
import zipfile
from http.server import ThreadingHTTPServer
from reversium.analyze import inspect_zip, MAX_FILE
from reversium.report import render
from reversium.__main__ import Handler
from reversium import __version__


def archive(files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as z:
        for name, value in files:
            z.writestr(name, value)
    buffer.seek(0)
    return buffer


class AnalysisTests(unittest.TestCase):
    def test_source_evidence(self):
        result = inspect_zip(archive([('app.py', 'import sqlite3\n@app.get("/hello")\ndef hello(): pass\n'), ('ui.ts', 'import x from "./lib";'), ('package.json', '{"dependencies":{"demo":"1"}}'), ('app.exe', b'MZ')]))
        self.assertEqual(result['summary']['binary_candidates'], 1)
        self.assertTrue(any(f['value'] == 'sqlite3' and f['evidence']['line'] == 1 for f in result['findings']))
        self.assertTrue(any(f['kind'] == 'route_candidate' and f['value'] == '/hello' for f in result['findings']))
        self.assertIn('<svg', render(result))

    def test_unsafe_paths(self):
        for name in ('../escape', '/absolute', 'C:/escape', '..\\escape'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                inspect_zip(archive([(name, 'x')]))

    def test_symlink(self):
        link = zipfile.ZipInfo('link')
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        with self.assertRaises(ValueError):
            inspect_zip(archive([(link, 'target')]))

    def test_duplicate(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            data = archive([('x', 'a'), ('x', 'b')])
        with self.assertRaises(ValueError):
            inspect_zip(data)

    def test_large_content_skipped(self):
        report = inspect_zip(archive([('large.py', 'x' * (MAX_FILE + 1))]))
        self.assertEqual(report['findings'], [])
        self.assertTrue(report['warnings'])

    def test_html_escape(self):
        report = inspect_zip(archive([('<script>.py', 'import os')]))
        self.assertNotIn('<script>.py', render(report))
        self.assertIn('&lt;script&gt;.py', render(report))

    def test_invalid_python_and_manifest(self):
        report = inspect_zip(archive([('broken.py', 'def :'), ('package.json', '{broken')]))
        self.assertEqual(len(report['warnings']), 2)

    def test_http(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f'http://127.0.0.1:{server.server_port}'
        try:
            connection = http.client.HTTPConnection('127.0.0.1', server.server_port)
            connection.request('GET', '/')
            self.assertIn(b'Reversium', connection.getresponse().read())
            connection.request('GET', '/example')
            sample = connection.getresponse().read()
            self.assertIn(b'Feature traced through code', sample)
            self.assertIn(b'role="tablist" aria-label="Report sections">', sample)
            connection.request('GET', '/version')
            self.assertEqual(json.loads(connection.getresponse().read())['version'], __version__)
            data = archive([('a.py', 'import os')]).getvalue()
            connection.request('POST', '/analyze', body=data, headers={'Content-Type': 'application/zip'})
            self.assertIn(b'a.py:1', connection.getresponse().read())
            connection.request('POST', '/analyze', body=data, headers={'Origin': 'https://example.com'})
            response = connection.getresponse()
            self.assertEqual(response.status, 403)
            response.read()
            connection.close()
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    unittest.main()

