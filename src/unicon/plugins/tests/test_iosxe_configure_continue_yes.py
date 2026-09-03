"""Unit tests for IOS-XE continue_yes pattern and statement."""

import re
import unittest
from unittest.mock import MagicMock

from unicon.plugins.iosxe.patterns import IosXEPatterns
from unicon.plugins.iosxe.service_statements import configure_statement_list, continue_yes


class TestContinueYes(unittest.TestCase):

    def test_pattern_matches_prompt(self):
        """Pattern must match the Continue? [yes]: prompt."""
        pattern = IosXEPatterns().continue_yes
        self.assertIsNotNone(re.search(pattern, 'Continue? [yes]: '))

    def test_statement_in_configure_statement_list(self):
        """continue_yes must be present in configure_statement_list."""
        self.assertIn(continue_yes, configure_statement_list)

    def test_statement_action_sends_yes(self):
        """Statement action must send 'yes' to accept the prompt."""
        mock_spawn = MagicMock()
        continue_yes.action(mock_spawn, **continue_yes.args)
        mock_spawn.sendline.assert_called_once_with('yes')


if __name__ == '__main__':
    unittest.main()
