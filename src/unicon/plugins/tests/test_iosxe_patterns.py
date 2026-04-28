"""
Unit tests for IOS-XE patterns.

Tests to ensure patterns like disable_prompt do not incorrectly match
rommon prompts or other unintended strings.
"""

import unittest
import re
from unicon.plugins.generic.settings import GenericSettings
from unicon.plugins.iosxe.patterns import IosXEPatterns
from unicon.eal.backend.spawn import RawSpawn


class DummySpawn(RawSpawn):
    """Minimal spawn implementation for exercising backend match logic."""

    def _send(self, command, *args, **kwargs):
        return True

    def read_update_buffer(self, size=None):
        return False

    def is_readable(self, timeout=0.01):
        return False

    def is_writable(self, timeout=0.01):
        return True

    def close(self, *args, **kwargs):
        return True


class TestIosXEDisablePrompt(unittest.TestCase):
    """Test cases for IOS-XE disable_prompt pattern."""

    def setUp(self):
        """Set up test patterns."""
        self.patterns = IosXEPatterns()
        self.disable_pattern = self.patterns.disable_prompt
        self.settings = GenericSettings()

    def _match_with_backend(self, pattern, buffer):
        """Mirror backend prompt matching via RawSpawn.match_buffer()."""
        spawn = DummySpawn(
            spawn_command='',
            settings=self.settings,
            match_mode_detect=True,
        )
        spawn.buffer = buffer
        return spawn.match_buffer(pattern) is not False

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

    def test_disable_prompt_does_not_match_master_key_warning_line(self):
        """Test backend prompt matching ignores the master-key warning line."""
        warning_buffer = (
            'User Access Verification\r\n'
            'Username: lab\r\n'
            'Password: \r\n'
            '% WARNING: The master key is not configured, so passwords/secrets '
            'might not be encrypted.\r\n'
            'Configure the master key by using the following command: '
            '"key config-key password-encrypt <encryption-key>'
        )

        disable_pattern = self.disable_pattern.replace(
            '%N', self.settings.DEFAULT_LEARNED_HOSTNAME
        )
        self.assertFalse(
            self._match_with_backend(disable_pattern, warning_buffer),
            "Pattern should NOT match the master-key warning buffer when %N "
            "is replaced with DEFAULT_LEARNED_HOSTNAME"
        )


if __name__ == '__main__':
    unittest.main()
