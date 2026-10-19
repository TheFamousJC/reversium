import unittest
from scripts.check_deployment import ROOT,PUBLIC,verify


class DeploymentTests(unittest.TestCase):
    def test_current_public_assets_match(self):
        self.assertEqual(verify('https://example.test/app',lambda p:(ROOT/p).read_bytes())['assets_checked'],len(PUBLIC))

    def test_stale_page_and_corrupt_engine_are_rejected(self):
        for changed in ('web/index.html','web/engine.zip','output/pdf/Reversium-Feature-List.pdf'):
            with self.subTest(asset=changed):
                with self.assertRaisesRegex(ValueError,'Stale or different'):
                    verify('https://example.test/app',lambda p:b'wrong' if p==changed else (ROOT/p).read_bytes())

    def test_credentials_and_nonlocal_plain_http_are_refused(self):
        for base in ('http://example.test','https://user:secret@example.test','https://example.test/?private=yes'):
            with self.assertRaises(ValueError):verify(base,lambda p: b'')
