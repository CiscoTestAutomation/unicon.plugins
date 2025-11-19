"""
Unit tests for IOS-XE patterns.

Tests to ensure patterns like disable_prompt do not incorrectly match
rommon prompts or other unintended strings.
"""

import unittest
import re
from unicon.plugins.iosxe.patterns import IosXEPatterns


class TestIosXEDisablePrompt(unittest.TestCase):
    """Test cases for IOS-XE disable_prompt pattern."""

    def setUp(self):
        """Set up test patterns."""
        self.patterns = IosXEPatterns()
        self.disable_pattern = self.patterns.disable_prompt

    def test_disable_prompt_matches_valid_prompts(self):
        """Test that disable_prompt matches valid disable mode prompts."""
        valid_prompts = [
            'Router>',
            'Switch>',
            'ios>',
            'wlc>',
            'WLC>',
            'RouterRP>',
            'Router1>',
            'Switch2>',
            'Router(boot)>',
            'Router(standby)>',
            'Router-stby>',
            'Router-standby>',
            'Router(recovery-mode)>',
            'Router(rp-rec-mode)>'
        ]
        
        for prompt in valid_prompts:
            with self.subTest(prompt=prompt):
                match = re.search(self.disable_pattern, prompt)
                self.assertIsNotNone(match, 
                    f"Pattern should match valid disable prompt: {prompt}")

    def test_disable_prompt_does_not_match_rommon_prompts(self):
        """Test that disable_prompt does NOT match rommon prompts."""
        rommon_prompts = [
            'rommon>',
            'rommon 1>',
            'rommon 2 >',
            'rommon>',
            'switch:',
            'grub>',
            'grub >',
        ]
        
        for prompt in rommon_prompts:
            with self.subTest(prompt=prompt):
                match = re.search(self.disable_pattern, prompt)
                self.assertIsNone(match, 
                    f"Pattern should NOT match rommon prompt: {prompt}")


if __name__ == '__main__':
    unittest.main()
