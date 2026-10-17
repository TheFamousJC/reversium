import unittest
from reversium.owner_summary import owner_summary


class OwnerSummaryTests(unittest.TestCase):
    def test_profile_clues_link_to_real_evidence_without_runtime_claims(self):
        findings = [{'kind': 'dependency', 'value': 'react', 'evidence': {'file': '<private>.json', 'line': 2}}]
        output = owner_summary({'findings': findings})
        self.assertIn('may include an interactive website', output)
        self.assertIn('#finding-0', output)
        self.assertIn('&lt;private&gt;.json:2', output)
        self.assertIn('did not install', output)
        self.assertNotIn('server behind', output)

    def test_arbitrary_text_does_not_establish_application_profile(self):
        output = owner_summary({'findings': [{'kind': 'string', 'value': 'react', 'evidence': {'file': 'a'}}]})
        self.assertIn('did not establish a simple application profile', output)
        self.assertNotIn('#finding-', output)
