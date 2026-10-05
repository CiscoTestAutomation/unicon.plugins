"""Unittests for the IOS-XE Cat9K C9800-CL plugin."""

import unittest
from unittest.mock import Mock

import unicon
from unicon import Connection
from unicon.plugins.generic.service_implementation import BashService
from unicon.plugins.iosxe.cat9k.c9800.c9800_cl import (
    IosXEc9800CLSingleRpConnection,
)
from unicon.plugins.iosxe.cat9k.c9800.c9800_cl.statemachine import (
    IosXEc9800CLSingleRpStateMachine,
)
from unicon.plugins.iosxe.cat9k.c9800.c9800_cl.statements import (
    boot_from_rommon,
)

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXEc9800CLStateMachine(unittest.TestCase):

    def _make_connection(self):
        return Connection(
            hostname='WLC',
            start=['mock_device_cli --os iosxe --state c9800_rommon_boot --hostname WLC'],
            os='iosxe',
            platform='cat9k',
            model='c9800',
            submodel='c9800_cl',
            log_buffer=True,
        )

    def test_connection_uses_c9800_cl_state_machine(self):
        self.assertIs(
            IosXEc9800CLSingleRpConnection.state_machine_class,
            IosXEc9800CLSingleRpStateMachine,
        )

    def test_connection_uses_c9800_cl_submodel_plugin(self):
        connection = self._make_connection()

        self.assertIsInstance(connection, IosXEc9800CLSingleRpConnection)
        self.assertEqual(connection.model, 'c9800')
        self.assertEqual(connection.submodel, 'c9800_cl')

    def test_bash_parse_adds_device_abstraction_tokens(self):
        device = Mock(
            os='iosxe',
            platform='cat9k',
            model='c9800',
            submodel='c9800_cl',
            pid='C9800-CL-K9',
        )
        connection = Mock(device=device)
        connection.settings.CONSOLE_TIMEOUT = 30
        console = BashService.ContextMgr(connection)

        console.parse('show version')

        device.parse.assert_called_once_with(
            'show version',
            abstract={
                'os': ['iosxe', 'linux'],
                'platform': 'cat9k',
                'model': 'c9800',
                'submodel': 'c9800_cl',
                'pid': 'C9800-CL-K9',
            },
        )

    def test_bash_parse_omits_undefined_submodel(self):
        device = Mock(
            os='iosxe',
            platform='cat9k',
            model='c9800',
            submodel=None,
            pid='C9800-80-K9',
        )
        connection = Mock(device=device)
        connection.settings.CONSOLE_TIMEOUT = 30
        console = BashService.ContextMgr(connection)

        console.parse('show version')

        device.parse.assert_called_once_with(
            'show version',
            abstract={
                'os': ['iosxe', 'linux'],
                'platform': 'cat9k',
                'model': 'c9800',
                'pid': 'C9800-80-K9',
            },
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
