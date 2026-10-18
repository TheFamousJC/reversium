import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from reversium.qemu_lab import argv, sanitize_delivery, probe_tudela, bundle_files, Guest


class QemuLabTests(unittest.TestCase):
    def test_profile_has_no_network_share_disk_or_remote_control(self):
        with tempfile.TemporaryDirectory() as d:
            lab=Path(d);args=argv(lab,lab/'input.iso')
            for flag in ('-nodefaults','-no-user-config','-no-reboot'):self.assertIn(flag,args)
            self.assertEqual(args[args.index('-nic')+1],'none')
            self.assertEqual(args[args.index('-display')+1],'none')
            self.assertEqual(args[args.index('-monitor')+1],'none')
            self.assertFalse(any(flag in args for flag in ('-netdev','-fsdev','-virtfs','-spice','-vnc','-qmp','-usbdevice')))
            self.assertTrue(all(x.endswith('format=raw,media=cdrom,readonly=on') for i,x in enumerate(args) if i and args[i-1]=='-drive'))
            with self.assertRaises(ValueError):argv(lab,lab.parent/'outside.iso')
            accelerated=argv(lab,accelerator='whpx')
            self.assertEqual(accelerated[accelerated.index('-accel')+1],'whpx')
            with self.assertRaises(ValueError):argv(lab,accelerator='automatic')

    def test_delivery_sanitization_stays_in_memory_and_omits_common_credentials(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:
            z.writestr('app/.env','SECRET=never-copy')
            z.writestr('app/.npmrc','token=never-copy')
            z.writestr('app/key.pem','private-key')
            z.writestr('app/main.py','x=1')
        stream.seek(0)
        data,sha,omitted=sanitize_delivery(stream)
        with zipfile.ZipFile(io.BytesIO(data)) as z:self.assertEqual(z.namelist(),['app/main.py'])
        self.assertEqual(len(sha),64);self.assertEqual(len(omitted),3)

    def test_unsafe_archives_and_red_signals_do_not_enter_guest(self):
        for name in ('../escape.py','invoice.pdf.exe'):
            stream=io.BytesIO()
            with zipfile.ZipFile(stream,'w') as z:z.writestr(name,b'MZ')
            stream.seek(0)
            with self.assertRaises(ValueError):sanitize_delivery(stream)

    @patch('reversium.qemu_lab.verify_lab',side_effect=lambda p:Path(p))
    @patch('reversium.qemu_lab.self_test',return_value={'passed':False})
    @patch('reversium.qemu_lab.bundle_files')
    def test_failed_isolation_gate_cannot_load_application(self,bundle,*mocks):
        with self.assertRaises(RuntimeError):probe_tudela('unused','unused.zip')
        bundle.assert_not_called()

    def test_guest_deadlines_are_bounded_before_start(self):
        for seconds in (0,601):
            with self.assertRaises(ValueError):Guest('unused',seconds=seconds)

    def test_unreviewed_project_profile_is_refused_before_cache_loading(self):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:
            z.writestr('project/package.json','{"scripts":{"build":"arbitrary","start":"arbitrary"}}')
            z.writestr('project/package-lock.json','{"packages":{}}')
        stream.seek(0)
        with self.assertRaisesRegex(ValueError,'reviewed Tudela'):
            bundle_files('unused',stream)

    def test_runtime_profile_installs_do_not_disable_package_trust(self):
        source=Path('reversium/qemu_lab.py').read_text(encoding='utf-8')
        self.assertNotIn('--allow-untrusted',source)
        self.assertIn('apk add --force-non-repository --no-network',source)

    def test_platform_filter_skips_incompatible_optional_descendants(self):
        from scripts.prepare_tudela_offline import npm_entries
        lock={'packages':{'':{},'node_modules/wasm':{'cpu':['wasm32']},'node_modules/wasm/node_modules/bundled':{'version':'1'},'node_modules/ok':{'resolved':'https://registry.npmjs.org/ok/-/ok-1.tgz','integrity':'sha512-YQ==','os':['!win32']}}}
        self.assertEqual([e['path'] for e in npm_entries(lock)],['node_modules/ok'])
        lock['packages']['node_modules/ok']['resolved']='http://127.0.0.1/private'
        with self.assertRaises(ValueError):npm_entries(lock)
