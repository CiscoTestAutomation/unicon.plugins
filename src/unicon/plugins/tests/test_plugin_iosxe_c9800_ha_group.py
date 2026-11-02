"""Unit tests for the IOS-XE Cat9K C9800 HA group plugin."""

import unittest
from unittest.mock import MagicMock

import unicon
from unicon import Connection
from unicon.plugins.iosxe.cat9k.c9800 import IosXEc9800DualRPConnection
from unicon.plugins.iosxe.cat9k.c9800.ha_group import (
    IosXEc9800HAGroupConnection,
)
from unicon.plugins.tests.mock.mock_device_iosxe import (
    MockDeviceTcpWrapperIOSXE,
)
from unicon.plugins.tests.mock.mock_device_iosxe_cat9k import (
    MockDeviceTcpWrapperIOSXECat9k,
)


unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXEc9800HAGroupPlugin(unittest.TestCase):

    @staticmethod
    def _make_connection(**kwargs):
        return Connection(
            hostname='WLC',
            start=['mock_device_cli', 'mock_device_cli'],
            os='iosxe',
            platform='cat9k',
            model='c9800',
            chassis_type='ha_group',
            **kwargs,
        )

    def test_physical_c9800_selects_ha_group_plugin(self):
        connection = self._make_connection()

        self.assertIsInstance(connection, IosXEc9800HAGroupConnection)
        self.assertEqual(connection.os, 'iosxe')
        self.assertEqual(connection.platform, 'cat9k')
        self.assertEqual(connection.model, 'c9800')
        self.assertEqual(connection.chassis_type, 'ha_group')

    def test_c9800_cl_falls_back_to_c9800_ha_group_plugin(self):
        connection = self._make_connection(submodel='c9800_cl')

        self.assertIsInstance(connection, IosXEc9800HAGroupConnection)

    def test_ha_group_inherits_c9800_dual_rp_implementation(self):
        self.assertTrue(
            issubclass(
                IosXEc9800HAGroupConnection,
                IosXEc9800DualRPConnection,
            )
        )

    def test_connect_ha_pair(self):
        mock_device = MockDeviceTcpWrapperIOSXECat9k(
            hostname='WLC114',
            port=0,
            state=(
                'cat9k_ha_active_enable,'
                'cat9k_ha_standby_disable_locked'
            ),
        )
        mock_device.start()
        connection = Connection(
            hostname='ha_WLC114_WLC115',
            start=[
                'telnet 127.0.0.1 {}'.format(mock_device.ports[0]),
                'telnet 127.0.0.1 {}'.format(mock_device.ports[1]),
            ],
            os='iosxe',
            platform='cat9k',
            model='c9800',
            chassis_type='ha_group',
            log_buffer=True,
        )
        connection.device = MagicMock()
        connection.device.credentials = {}
        connection.device.execute.return_value = (
            'my state = 13 -ACTIVE\n'
            'peer state = 8 -STANDBY HOT\n'
        )

        try:
            connection.connect()

            self.assertEqual(connection.active.alias, 'a')
            self.assertEqual(connection.standby.alias, 'b')
            self.assertEqual(
                connection.standby.state_machine.current_state,
                'enable',
            )
        finally:
            connection.disconnect()
            mock_device.stop()

    def test_connect_standalone_pair(self):
        mock_devices = [
            MockDeviceTcpWrapperIOSXE(
                hostname='WLC114', port=0, state='enable_asr'
            ),
            MockDeviceTcpWrapperIOSXE(
                hostname='WLC115', port=0, state='enable_asr'
            ),
        ]
        for mock_device in mock_devices:
            mock_device.start()

        connection = Connection(
            hostname='ha_WLC114_WLC115',
            start=[
                'telnet 127.0.0.1 {}'.format(mock_device.ports[0])
                for mock_device in mock_devices
            ],
            os='iosxe',
            platform='cat9k',
            model='c9800',
            chassis_type='ha_group',
            log_buffer=True,
        )
        connection.device = MagicMock()
        connection.device.credentials = {}
        connection.device.execute.return_value = (
            'my state = 13 -ACTIVE\n'
            'peer state = 0 -DISABLED\n'
        )

        try:
            connection.connect()

            self.assertEqual(connection.a.state_machine.current_state, 'enable')
            self.assertEqual(connection.b.state_machine.current_state, 'enable')
            self.assertEqual(connection.active.alias, 'a')
            self.assertEqual(connection.standby.alias, 'b')
        finally:
            connection.disconnect()
            for mock_device in mock_devices:
                mock_device.stop()


if __name__ == '__main__':
    unittest.main()
