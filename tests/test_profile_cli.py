"""Neutral names retain the fixed backend, without running a guest in tests."""
import contextlib
import io
import unittest
from unittest.mock import patch
from reversium.__main__ import main


class ProfileCliTests(unittest.TestCase):
    def test_neutral_and_legacy_flags_dispatch_to_same_reviewed_profile(self):
        for flag,service in [('--sandbox-project',False),('--sandbox-tudela',False),('--sandbox-project-services',True),('--sandbox-tudela-tour',True)]:
            with self.subTest(flag=flag), patch('sys.argv',['reversium',flag,'your-package.zip']), patch('reversium.qemu_lab.probe_tudela',return_value={}) as backend, contextlib.redirect_stdout(io.StringIO()):
                main()
                backend.assert_called_once_with('reports/qemu-lab','your-package.zip',accelerator='tcg',tour=service)

    def test_conflicting_profile_actions_do_not_run_a_guest(self):
        with patch('sys.argv',['reversium','--sandbox-project','one.zip','--sandbox-project-services','two.zip']), patch('reversium.qemu_lab.probe_tudela') as backend, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):main()
            backend.assert_not_called()

    def test_help_shows_only_neutral_profile_names(self):
        output=io.StringIO()
        with patch('sys.argv',['reversium','--help']), contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit):main()
        self.assertIn('--sandbox-project',output.getvalue())
        self.assertNotIn('tudela',output.getvalue().lower())
