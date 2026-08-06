"""
Unit tests for configure_yes_no_stmt pattern and behavior.

Tests to ensure the configure_yes_no pattern:
1. Matches the slash variant [yes/no]: prompts
2. Does NOT match the comma variant [yes,no] prompts
3. Is included in configure_statement_list
"""

import unittest
import re

from unicon.plugins.generic.service_patterns import reload_patterns
from unicon.plugins.generic.service_statements import (
    configure_statement_list,
    configure_yes_no_stmt,
)


class TestConfigureYesNoPattern(unittest.TestCase):
    """Test cases for configure_yes_no pattern."""

    def setUp(self):
        """Set up test patterns."""
        self.pattern = reload_patterns.configure_yes_no

    def test_pattern_matches_slash_variant_prompts(self):
        """Test that pattern matches [yes/no]: slash variant prompts."""
        valid_prompts = [
            'Continue with master key deletion ? [yes/no]: ',
            'Continue with master key deletion ? [yes/No]: ',
            'WARNING: Continue? [yes/no]: ',
            'Do you want to proceed? [yes/no]: ',
            'Are you sure? [yes/no]:',
            '[yes/no]: ',
            'Some text [yes/no]:',
            'Continue with master key deletion ? [yes/no]:',
        ]

        for prompt in valid_prompts:
            with self.subTest(prompt=prompt):
                match = re.search(self.pattern, prompt)
                self.assertIsNotNone(
                    match,
                    f"Pattern should match slash variant prompt: {prompt}"
                )

    def test_pattern_does_not_match_comma_variant_prompts(self):
        """Test that pattern does NOT match [yes,no] comma variant prompts.

        The comma variant is used by other platform-specific dialogs
        (e.g., SDWAN/IOSXE reload confirmations) and should not be
        handled by this generic configure statement.
        """
        comma_prompts = [
            'Reload node ? [no,yes]',
            'Proceed with reload? [yes,no]',
            'Confirm action [yes,no]:',
            '[yes,no]: ',
            'Do you want to continue? [yes,no]',
        ]

        for prompt in comma_prompts:
            with self.subTest(prompt=prompt):
                match = re.search(self.pattern, prompt)
                self.assertIsNone(
                    match,
                    f"Pattern should NOT match comma variant prompt: {prompt}"
                )

    def test_pattern_does_not_match_y_n_prompts(self):
        """Test that pattern does NOT match [y/n] or (y/n) prompts.

        These short-form prompts are handled by other statements.
        """
        short_prompts = [
            'Continue? [y/n]: ',
            'Proceed? (y/n): ',
            '[y/n]: ',
            'Are you sure? [y/N]: ',
        ]

        for prompt in short_prompts:
            with self.subTest(prompt=prompt):
                match = re.search(self.pattern, prompt)
                self.assertIsNone(
                    match,
                    f"Pattern should NOT match short-form prompt: {prompt}"
                )

    def test_pattern_does_not_match_confirm_prompts(self):
        """Test that pattern does NOT match [confirm] prompts."""
        confirm_prompts = [
            'Proceed with reload? [confirm]',
            '[confirm]',
        ]

        for prompt in confirm_prompts:
            with self.subTest(prompt=prompt):
                match = re.search(self.pattern, prompt)
                self.assertIsNone(
                    match,
                    f"Pattern should NOT match confirm prompt: {prompt}"
                )


class TestConfigureYesNoStatement(unittest.TestCase):
    """Test cases for configure_yes_no_stmt."""

    def test_statement_in_configure_statement_list(self):
        """Test that configure_yes_no_stmt is in configure_statement_list."""
        self.assertIn(
            configure_yes_no_stmt,
            configure_statement_list,
            "configure_yes_no_stmt should be in configure_statement_list"
        )

    def test_statement_has_correct_pattern(self):
        """Test that statement uses the correct pattern."""
        self.assertEqual(
            configure_yes_no_stmt.pattern,
            reload_patterns.configure_yes_no,
            "Statement should use reload_patterns.configure_yes_no pattern"
        )

    def test_statement_has_loop_continue_true(self):
        """Test that statement has loop_continue=True for dialog continuation."""
        self.assertTrue(
            configure_yes_no_stmt.loop_continue,
            "Statement should have loop_continue=True"
        )

    def test_statement_sends_yes_not_y(self):
        """Test that statement sends 'yes' instead of short form 'y'.

        Some devices reject the short form 'y' and require the full 'yes'.
        """
        self.assertEqual(
            configure_yes_no_stmt.args.get('response'),
            'yes',
            "Statement should send 'yes', not 'y' - some devices require full form"
        )


if __name__ == '__main__':
    unittest.main()
