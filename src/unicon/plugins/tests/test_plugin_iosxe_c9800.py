"""
Unittests for iosxe/cat9k/c9800 plugin (C9800-CL vWLC).
"""

import unittest
from unittest.mock import Mock

import unicon
from unicon import Connection
from unicon.plugins.iosxe.cat9k.c9800 import IosXEc9800SingleRpConnection
from unicon.plugins.iosxe.cat9k.c9800.statemachine import IosXEc9800SingleRpStateMachine
from unicon.plugins.iosxe.cat9k.c9800.statements import boot_from_rommon

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXEc9800StateMachine(unittest.TestCase):

    def _make_connection(self):
        return Connection(
            hostname='WLC',
            start=['mock_device_cli --os iosxe --state c9800_rommon_boot --hostname WLC'],
            os='iosxe',
            platform='cat9k',
            model='c9800',
            log_buffer=True,
        )

    def test_connection_uses_c9800_state_machine(self):
        self.assertIs(
            IosXEc9800SingleRpConnection.state_machine_class,
            IosXEc9800SingleRpStateMachine,
        )

    def test_rommon_pattern_includes_grub(self):
        c = self._make_connection()
        self.assertIn('grub', c.state_machine.get_state('rommon').pattern)

    def test_rommon_to_disable_path_uses_grub_boot_action(self):
        c = self._make_connection()
        path = c.state_machine.get_path('rommon', 'disable')
        self.assertIs(path.command, boot_from_rommon)

    def test_boot_from_rommon_sends_escape(self):
        spawn = Mock()
        boot_from_rommon(Mock(), spawn, {})
        spawn.send.assert_called_once_with('\x1b')


if __name__ == '__main__':
    unittest.main()

