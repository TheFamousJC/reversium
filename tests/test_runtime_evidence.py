import unittest
from reversium.runtime_evidence import portable_result,ISOLATION_KEYS,APPLICATION_KEYS

class PortableRuntimeEvidenceTests(unittest.TestCase):
    def test_fixed_projection_excludes_logs_credentials_and_paths(self):
        raw={'delivery':{'source_archive_sha256':'a'*64,'sanitized_archive_sha256':'b'*64,'omitted_sensitive_or_generated_members':['private/.env']},'accelerator':'whpx','checks':{'frontend_build':True},'input_media_unchanged':True,'guest_process_stopped':True,'blocker':'private-key','raw_log':'secret','runtime_versions':['v24.18.1','11.11.0']}
        record=portable_result(raw,{'checks':dict.fromkeys(ISOLATION_KEYS,True)},'abcdef123456','2026-10-18T08:00:00Z')
        self.assertEqual(record['archive_sha256'],'a'*64)
        self.assertEqual(record['tested_input_sha256'],'b'*64)
        self.assertEqual(record['omitted_member_count'],1)
        self.assertEqual(set(record['checks']),set(APPLICATION_KEYS))
        self.assertIsNone(record['checks']['backend_compile'])
        self.assertTrue(record['checks']['frontend_build'])
        self.assertNotIn('private',str(record));self.assertNotIn('secret',str(record))
        self.assertNotIn('passed',record)

    def test_report_keeps_runtime_record_separate_from_static_payload(self):
        from reversium.analyze import inspect_zip
        from reversium.sample import javascript_sample_archive
        from reversium.report import render
        report=inspect_zip(javascript_sample_archive())
        page=render(report)
        self.assertIn('id="runtime-record-data" type="application/json">null',page)
        self.assertIn('Static setup clues',page)
        self.assertNotIn('runtime_test_record',report)

    def test_guest_copy_and_identity_use_one_snapshot_even_if_original_changes(self):
        import hashlib,io,tempfile,zipfile
        from pathlib import Path
        from unittest.mock import patch
        from reversium.analyze import inspect_zip
        from reversium.qemu_lab import sanitize_delivery
        def archive(text):
            stream=io.BytesIO()
            with zipfile.ZipFile(stream,'w') as z:z.writestr('app/main.py',text)
            return stream.getvalue()
        original=archive('first = True');replacement=archive('second = True')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'delivery.zip';path.write_bytes(original)
            def inspect_then_replace(stream):
                report=inspect_zip(stream);path.write_bytes(replacement);return report
            with patch('reversium.analyze.inspect_zip',side_effect=inspect_then_replace):
                data,sha,_=sanitize_delivery(path)
            self.assertEqual(sha,hashlib.sha256(original).hexdigest())
            with zipfile.ZipFile(io.BytesIO(data)) as z:self.assertEqual(z.read('app/main.py'),b'first = True')
