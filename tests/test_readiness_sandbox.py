import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree
from reversium.analyze import inspect_zip
from reversium.report import render
from reversium.sandbox import capabilities, prepare


class ReadinessSandboxTests(unittest.TestCase):
    def test_inventory_clues_are_not_runtime_claims_or_secret_values(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:
            for name,data in [('package.json','{}'),('package-lock.json','{}'),('.env.example','TOKEN=private-value'),('migrations/one.sql','create table sample(id int);'),('backup.ps1','echo ok')]:z.writestr(name,data)
        stream.seek(0);report=inspect_zip(stream)
        checks=report['readiness_plan']['checks']
        self.assertEqual(len(checks),8)
        self.assertEqual(checks[1]['files'],['package-lock.json'])
        self.assertFalse(checks[-1]['files'])
        self.assertNotIn('private-value',json.dumps(report))
        page=render(report)
        self.assertIn('Not runtime verified',page)
        self.assertIn('id="tab-readiness"',page)
        self.assertIn('.handover-task,.readiness-card{background:#fff',page)

    @patch('reversium.sandbox.shutil.which',return_value=None)
    @patch('reversium.sandbox.platform.system',return_value='Linux')
    def test_missing_backend_is_reported_without_claiming_execution(self,*args):
        status=capabilities()
        self.assertFalse(status['execution_enabled'])
        self.assertFalse(status['qemu_executable'])
        self.assertIn('untested',status['summary'])

    def test_profiles_have_no_network_host_mapping_or_startup_commands(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'new'
            prepare(target)
            xml=ElementTree.parse(target/'blank-offline.wsb').getroot()
            for key in ['Networking','ClipboardRedirection','AudioInput','VideoInput','PrinterRedirection','vGPU']:
                self.assertEqual(xml.findtext(key),'Disable')
            self.assertIsNone(xml.find('MappedFolders'))
            self.assertIsNone(xml.find('LogonCommand'))
            draft=json.loads((target/'qemu-arguments-DRAFT.json').read_text())
            self.assertIn('-nodefaults',draft['argv'])
            self.assertEqual(draft['argv'][draft['argv'].index('-nic')+1],'none')
            self.assertFalse(any(x in draft['argv'] for x in ['-fsdev','-virtfs','-netdev']))
            with self.assertRaises(FileExistsError):prepare(target)
