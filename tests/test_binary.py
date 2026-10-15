import struct
import unittest
from binary_fixtures import pe_fixture, elf_fixture, java_fixture, container_fixture
from test_reversium import archive
from reversium.analyze import inspect_zip
from reversium.binary import inspect_binary, MAX_STRINGS
from reversium.report import render
from reversium.source import compare_reports


class BinaryTests(unittest.TestCase):
    def test_pe_imports_and_managed_header(self):
        metadata, findings = inspect_binary(pe_fixture(), 'renamed.data')
        self.assertEqual(metadata['format'], 'PE')
        self.assertEqual(metadata['architecture'], 'x86-64')
        self.assertEqual(metadata['status'], 'complete')
        self.assertTrue(metadata['managed'])
        self.assertTrue(any(f['value'] == 'KERNEL32.dll' and f['evidence']['offset'] == 592 for f in findings))
        self.assertNotIn('user:pass', str(findings))

    def test_elf_imports(self):
        metadata, findings = inspect_binary(elf_fixture(), 'program')
        self.assertEqual(metadata['status'], 'complete')
        self.assertEqual(metadata['bits'], 64)
        self.assertTrue(any(f['kind'] == 'binary_import' and f['value'] == 'libc.so.6' for f in findings))

    def test_java_references(self):
        metadata, findings = inspect_binary(java_fixture(), 'renamed.bin')
        self.assertEqual(metadata['major'], 61)
        self.assertTrue(any(f['kind'] == 'binary_class_reference' and f['value'] == 'java/lang/Object' for f in findings))

    def test_elf_32_big_endian_header(self):
        ident = b'\x7fELF\x01\x02\x01' + b'\0' * 9
        data = struct.pack('>16sHHIIIIIHHHHHH', ident, 2, 40, 1, 0, 0, 0, 0, 52, 0, 0, 40, 0, 0)
        metadata, _ = inspect_binary(data, 'arm-binary')
        self.assertEqual(metadata['bits'], 32)
        self.assertEqual(metadata['architecture'], 'ARM')
        self.assertEqual(metadata['status'], 'complete')
        self.assertTrue(metadata['notes'])

    def test_dex_and_macho_identification(self):
        dex = bytearray(112)
        dex[:8] = b'dex\n035\0'
        struct.pack_into('<II', dex, 36, 112, 0x12345678)
        metadata, _ = inspect_binary(bytes(dex), 'classes.dex')
        self.assertEqual(metadata['runtime'], 'Android DEX')
        self.assertEqual(metadata['status'], 'complete')
        metadata, _ = inspect_binary(b'\xcf\xfa\xed\xfe' + b'\0' * 28, 'library')
        self.assertEqual(metadata['format'], 'Mach-O')
        self.assertEqual(metadata['status'], 'complete')

    def test_containers_not_recursively_analyzed(self):
        for apk, expected in ((True, 'APK container'), (False, 'JAR-like container')):
            metadata, findings = inspect_binary(container_fixture(apk), 'package')
            self.assertEqual(metadata['format'], expected)
            self.assertTrue(any(f['kind'] == 'container_member' for f in findings))
            self.assertFalse(any(f['kind'] == 'binary_class_reference' for f in findings))

    def test_truncated_and_unknown_binaries(self):
        for value in (b'MZ', b'\x7fELF', b'\xca\xfe\xba\xbe\0\0\0\x3d', b'dex\n035\0'):
            metadata, findings = inspect_binary(value, 'bad.bin')
            self.assertEqual(metadata['status'], 'partial')
            self.assertTrue(metadata['notes'])
        metadata, _ = inspect_binary(b'not a real executable', 'fake.exe', True)
        self.assertEqual(metadata['status'], 'unsupported')
        self.assertIsNone(inspect_binary(b'ordinary text', 'file.txt'))

    def test_malformed_offsets_do_not_crash(self):
        data = bytearray(pe_fixture())
        struct.pack_into('<I', data, 0x3c, 0xfffffff0)
        self.assertEqual(inspect_binary(bytes(data), 'bad.exe')[0]['status'], 'partial')
        data = bytearray(elf_fixture())
        struct.pack_into('<Q', data, 40, 0xfffffff0)
        self.assertEqual(inspect_binary(bytes(data), 'bad.so')[0]['status'], 'partial')

    def test_strings_capped_and_credentials_omitted(self):
        metadata, findings = inspect_binary(b'MZ' + b'\0some string\0' * 100 + b'token=private', 'strings.exe')
        strings = [f for f in findings if f['kind'] == 'binary_string_candidate']
        self.assertLessEqual(len(strings), MAX_STRINGS)
        _, findings = inspect_binary(b'MZ\0token=private\0', 'secret.exe')
        self.assertNotIn('token=private', str(findings))

    def test_source_urls_emit_host_without_credentials(self):
        report = inspect_zip(archive([('app.py', 'url = "https://user:private@example.test/path?token=value"')]))
        hosts = [f['value'] for f in report['findings'] if f['kind'] == 'endpoint_host_candidate']
        self.assertEqual(hosts, ['https://example.test'])
        self.assertNotIn('private', str(report['findings']))

    def test_signature_detection_and_offset_html(self):
        report = inspect_zip(archive([('renamed.data', pe_fixture()), ('fake.exe', b'fake'), ('platform.class', java_fixture())]))
        self.assertEqual(report['summary']['binary_candidates'], 3)
        self.assertEqual(report['files'][0]['binary']['format'], 'PE')
        html = render(report)
        self.assertIn('byte 0x250', html)
        self.assertIn('Binary inspection', html)
        self.assertIn('Not verified:', html)
        self.assertEqual(compare_reports(report, report)['added_findings'], [])

    def test_platform_and_service_evidence(self):
        report = inspect_zip(archive([('requirements.txt', 'FastAPI\npsycopg>=3\nredis'), ('Dockerfile', 'FROM python:3.12\nRUN echo should-never-run'), ('compose.yaml', 'services:\n  db:\n    image: postgres:16')]))
        profile = report['platform']
        self.assertTrue(any(f['name'] == 'FastAPI web API' for f in profile['stack_candidates']))
        self.assertTrue(any(f['name'] == 'PostgreSQL' for f in profile['supporting_services']))
        self.assertTrue(any(f['name'] == 'postgres' for f in profile['supporting_services']))
        self.assertIn('Not verified:', profile['readiness'])

    def test_no_platform_evidence_is_unknown(self):
        profile = inspect_zip(archive([('readme.txt', 'hello')]))['platform']
        self.assertEqual(profile['supporting_services'], [])
        self.assertIn('not determined', profile['purpose'])

    def test_binary_hash_comparison(self):
        old = inspect_zip(archive([('app.exe', pe_fixture())]))
        new = inspect_zip(archive([('app.exe', pe_fixture() + b'\0changed')]))
        changes = compare_reports(new, old)
        self.assertEqual(changes['changed_files'], ['app.exe'])
        self.assertEqual(changes['changed_source_files'], [])


if __name__ == '__main__':
    unittest.main()
