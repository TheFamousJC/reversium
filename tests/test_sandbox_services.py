import hashlib,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from reversium.service_inputs import add_services

class SandboxServiceCacheTests(unittest.TestCase):
    def test_changed_offline_service_bytes_are_rejected_before_guest_input(self):
        with tempfile.TemporaryDirectory() as d:
            lab=Path(d);(lab/'services').mkdir();(lab/'services/auth.tar.xz').write_bytes(b'changed')
            with patch('reversium.service_inputs.PINNED',{'auth.tar.xz':hashlib.sha256(b'expected').hexdigest()}):
                with self.assertRaisesRegex(ValueError,'checksum mismatch'):add_services(lab,{})

    def test_oversized_runtime_manifest_is_rejected_without_loading_files(self):
        with tempfile.TemporaryDirectory() as d:
            lab=Path(d);(lab/'service-apks').mkdir();(lab/'service-apks/manifest.json').write_text(json.dumps([{}]*81))
            with patch('reversium.service_inputs.PINNED',{}):
                with self.assertRaisesRegex(ValueError,'count invalid'):add_services(lab,{})
