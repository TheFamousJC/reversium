import io
import unittest
import zipfile
from reversium.analyze import inspect_zip
from reversium.browser_report import render_browser

class BrowserTests(unittest.TestCase):
    def test_isolated_report_retains_evidence_without_cloud_controls(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:
            z.writestr('main.py','print("hello")')
        stream.seek(0)
        html=render_browser(inspect_zip(stream))
        self.assertIn("connect-src 'none'",html)
        self.assertIn('reversium-download',html)
        self.assertIn('id="report-data"',html)
        self.assertIn('id="panel-assistant"',html)
        self.assertIn('Manual handoff',html)
        self.assertIn('id="tab-help"',html)
        self.assertIn('Online and local editions',html)
        self.assertIn('Download user guide (PDF)',html)
        self.assertIn('Open PDF directly',html)
        self.assertIn("location.href==='about:srcdoc'",html)
        self.assertNotIn('/assistant/ask',html)
        self.assertIn('No account or AI connection',html)
        self.assertIn('data-subsection="architecture-',html)
        self.assertIn('data-subsection="coverage-',html)
        self.assertIn('class="inventory-numbers"',html)
        self.assertNotIn('<summary>Technical inventory numbers',html)

    def test_shipped_engine_contains_only_application_sources(self):
        with zipfile.ZipFile('web/engine.zip') as z:
            self.assertTrue(z.namelist())
            self.assertTrue(all(n.startswith('reversium/') and n.endswith('.py') for n in z.namelist()))
            self.assertNotIn('reversium/__main__.py',z.namelist())
