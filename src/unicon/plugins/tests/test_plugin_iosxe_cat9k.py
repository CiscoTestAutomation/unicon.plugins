"""
Unittests for iosxe/cat9k plugin
"""

import unittest
from unittest import mock


import unicon
from unicon import Connection
from unicon.eal.dialogs import Statement, Dialog
from unicon.plugins.tests.mock.mock_device_iosxe import MockDeviceTcpWrapperIOSXE
from unicon.plugins.tests.mock.mock_device_iosxe_cat9k import MockDeviceTcpWrapperIOSXECat9k
from unicon.core.errors import SubCommandFailure

from pyats.topology import loader

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXeCat9kPlugin(unittest.TestCase):

    def test_connect(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state c9k_login'],
                       os='iosxe',
                       platform='cat9k',
                       credentials=dict(default=dict(username='admin', password='cisco')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       log_buffer=True
                       )
        d.connect()
        d.disconnect()

    def test_connect_learn_hostname(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state c9k_login --hostname WLC'],
                       os='iosxe',
                       platform='cat9k',
                       credentials=dict(default=dict(username='admin', password='cisco')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       learn_hostname=True,
                       log_buffer=True
                       )
        try:
            d.connect()
            self.assertEqual(d.hostname, 'WLC')
        finally:
            d.disconnect()

    def test_connect_learn_hostname_config_mode(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state c9k_config --hostname c9300-55'],
                       os='iosxe',
                       platform='cat9k',
                       credentials=dict(default=dict(username='admin', password='cisco')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       learn_hostname=True,
                       log_buffer=True,
                       connection_timeout=3
                       )
        try:
            d.connect()
            self.assertEqual(d.hostname, 'c9300-55')
        finally:
            d.disconnect()

    def test_boot_from_rommon(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='cat9k_rommon')
        md.start()

        c = Connection(
            hostname='switch',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            platform='cat9k',
            settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             alt=dict(username='admin', password='lab'))
        )
        try:
            c.connect()
            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()
            md.stop()

    def test_connect_fallback(self):
        """
        Test the fallback credentials functionality for IOSXE Cat9k devices.

        This test verifies that when the default credentials fail to authenticate,
        the connection process falls back to the configured fallback credentials
        (set1) and successfully establishes a connection to the device.

        Expected behavior: Connection should succeed using fallback credentials
        when default credentials are not accepted by the device.
        """
        md = MockDeviceTcpWrapperIOSXE(port=0, state='c9k_login5', hostname='switch')
        md.start()

        testbed = """
        devices:
          R1:
            os: iosxe
            type: cat9k
            credentials:
                default:
                    username: admin
                    password: cisco
                set1:
                    username: cisco
                    password: cisco
            connections:
              defaults:
                class: unicon.Unicon
                fallback_credentials:
                    - set1
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
        """.format(md.ports[0])

        tb = loader.load(testbed)
        device = tb.devices.R1
        try:
            device.connect()
            self.assertEqual(device.state_machine.current_state, 'enable')
            self.assertIn('current_credentials', device.credentials)
            self.assertEqual(device.credentials['current_credentials']['username'], 'cisco')
            # Should match the fallback credential, not default
            self.assertEqual(device.credentials['current_credentials'], device.credentials['set1'])
        finally:
            device.disconnect()
            md.stop()

    def test_connect_fallback_login_handler(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='c9k_login6', hostname='switch')
        md.start()

        testbed = """
        devices:
          R1:
            os: iosxe
            type: cat9k
            credentials:
                default:
                    username: admin
                    password: cisco
                set1:
                    username: cisco
                    password: cisco
            connections:
              defaults:
                class: unicon.Unicon
                fallback_credentials:
                    - set1
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
        """.format(md.ports[0])

        tb = loader.load(testbed)
        device = tb.devices.R1
        try:
            device.connect()
            self.assertEqual(device.state_machine.current_state, 'enable')
        finally:
            device.disconnect()
            md.stop()

    def test_connect_login_creds(self):
        """
        Test that login_creds stores the last credential as current_credentials.

        This test verifies that when multiple credentials are specified in login_creds,
        the connection process correctly stores the last successfully used credential
        as the current_credentials in the device's credentials dictionary.

        Expected behavior:
        - TS credentials pass initially but are not stored as current_credentials
        - Default credentials are used for enable mode and stored as current_credentials
        - Device successfully connects and reaches enable state
        - current_credentials should reflect the 'default' credential set

        This ensures proper credential tracking for subsequent operations.
        """
        md = MockDeviceTcpWrapperIOSXE(port=0, state='c9k_login7', hostname='switch')
        md.start()

        testbed = """
        devices:
            R1:
                os: iosxe
                type: cat9k
                credentials:
                    default:
                        username: admin
                        password: cisco
                    ts:
                        username: ts_user
                        password: ts_pass
                connections:
                    defaults:
                        class: unicon.Unicon
                    a:
                        protocol: telnet
                        ip: 127.0.0.1
                        port: {}
                        login_creds: [ts, default]
        """.format(md.ports[0])

        tb = loader.load(testbed)
        device = tb.devices.R1
        try:
            device.connect()
            self.assertEqual(device.state_machine.current_state, 'enable')
            self.assertIn('current_credentials', device.credentials)
            self.assertEqual(device.credentials['current_credentials']['username'], 'admin')
            # Should match the 'default' credential, not 'ts'
            self.assertEqual(device.credentials['current_credentials'], device.credentials['default'])
        finally:
            device.disconnect()
            md.stop()

    def test_connect_login_creds_with_fallback(self):
        """
        Test login credentials with fallback mechanism for IOSXE Cat9k device connection.

        This test verifies the credential fallback behavior when multiple credential sets
        are configured and some fail during authentication:

        Expected behavior:
        - TS credentials pass initially
        - Default credentials fail (wrong password)
        - Fallback credentials are attempted and succeed
        - Fallback credentials are stored as current_credentials
        - Device successfully connects and reaches enable state
        """
        md = MockDeviceTcpWrapperIOSXE(port=0, state='c9k_login8', hostname='switch')
        md.start()

        testbed = """
        devices:
            R1:
                os: iosxe
                type: cat9k
                credentials:
                    default:
                        username: admin
                        password: wrong_password  # This will fail
                    ts:
                        username: ts_user
                        password: ts_pass
                    fallback_set:
                        username: fallback_user
                        password: fallback_pass
                connections:
                    defaults:
                        class: unicon.Unicon
                        fallback_credentials:
                            - fallback_set
                    a:
                        protocol: telnet
                        ip: 127.0.0.1
                        port: {}
                        login_creds: [ts, default]
        """.format(md.ports[0])

        tb = loader.load(testbed)
        device = tb.devices.R1
        try:
            device.connect()
            self.assertEqual(device.state_machine.current_state, 'enable')
            # Verify that fallback credential is stored as current_credentials
            # Since default failed and fallback succeeded, fallback_set should be stored
            self.assertIn('current_credentials', device.credentials)
            self.assertEqual(device.credentials['current_credentials']['username'], 'fallback_user')
            # Should match the fallback credential, not default or ts
            self.assertEqual(device.credentials['current_credentials'], device.credentials['fallback_set'])

        finally:
            device.disconnect()
            md.stop()

    def test_reload_image_from_rommon(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='cat9k_rommon')
        md.start()

        c = Connection(
            hostname='switch',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            platform='cat9k',
            mit=True,
            settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             alt=dict(username='admin', password='lab'))
        )
        try:
            c.connect()
            self.assertEqual(c.state_machine.current_state, 'rommon')
            c.execute('unlock flash:')
            c.settings.POST_RELOAD_WAIT = 1
            c.reload(image_to_boot='tftp://1.1.1.1/latest.bin')
            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()
            md.stop()

    def test_connect_cat9k_rommon_init(self):
        md = MockDeviceTcpWrapperIOSXECat9k(port=0, state='cat9k_rommon', hostname='R1')
        md.start()

        con = Connection(
            hostname='R1',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
            ],
            os='iosxe',
            platform='cat9k',
            connection_timeout=10,
            settings={'FIND_BOOT_IMAGE': False},
            credentials=dict(default=dict(password='cisco')),
            log_buffer=True,
            image_to_boot='tftp://1.1.1.1/cat9k_iosxe.SSA.bin',
        )
        try:
            con.connect()
        except Exception:
            raise
        finally:
            con.disconnect()
            md.stop()

    def test_connect_cat9k_rommon_init_commands(self):
        md = MockDeviceTcpWrapperIOSXECat9k(port=0, state='cat9k_rommon', hostname='R1')
        md.start()

        con = Connection(
            hostname='R1',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
            ],
            os='iosxe',
            platform='cat9k',
            connection_timeout=10,
            settings={
                'FIND_BOOT_IMAGE': False,
                'ROMMON_INIT_COMMANDS': [
                    'set',
                    'ping 1.1.1.1'
                ]
            },
            credentials=dict(default=dict(password='cisco')),
            log_buffer=True,
            image_to_boot='tftp://1.1.1.1/cat9k_iosxe.SSA.bin',
        )
        try:
            con.connect()
        except Exception:
            raise
        finally:
            con.disconnect()
            md.stop()

    def test_connect_cat9k_ha_rommon_init_commands(self):
        md = MockDeviceTcpWrapperIOSXECat9k(port=0, state='cat9k_ha_active_rommon,cat9k_ha_standby_rommon')
        md.start()

        c = Connection(
            hostname='switch',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1]),
            ],
            os='iosxe',
            platform='cat9k',
            log_buffer=True,
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             alt=dict(username='admin', password='lab')),
            settings={
                'FIND_BOOT_IMAGE': False,
                'ROMMON_INIT_COMMANDS': [
                    'set',
                    'ping 1.1.1.1'
                ]
            }
        )
        try:
            c.connect()
            self.assertEqual(c.state_machine.current_state, 'enable')
            self.assertEqual(c.hostname, 'switch')
        finally:
            c.disconnect()
            md.stop()

    def test_connect_cat9k_ha_rommon_init_commands_learn_hostname(self):
        md = MockDeviceTcpWrapperIOSXECat9k(port=0, state='cat9k_ha_active_rommon,cat9k_ha_standby_rommon')
        md.start()

        c = Connection(
            hostname='switch',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1]),
            ],
            os='iosxe',
            platform='cat9k',
            log_buffer=True,
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             alt=dict(username='admin', password='lab')),
            settings={
                'FIND_BOOT_IMAGE': False,
                'ROMMON_INIT_COMMANDS': [
                    'set',
                    'ping 1.1.1.1'
                ]
            },
            learn_hostname=True
        )
        try:
            c.connect()
            self.assertEqual(c.state_machine.current_state, 'enable')
            self.assertEqual(c.hostname, 'Router')
        finally:
            c.disconnect()
            md.stop()


    def test_connect_cat9k_ha_learn_hostname(self):
        md = MockDeviceTcpWrapperIOSXECat9k(hostname='R1', port=0, state='cat9k_ha_active_enable,cat9k_ha_standby_enable')
        md.start()

        c = Connection(
            hostname='switch',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1]),
            ],
            os='iosxe',
            platform='cat9k',
            log_buffer=True,
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             alt=dict(username='admin', password='lab')),
            learn_hostname=True
        )
        try:
            c.connect()
            self.assertEqual(c.state_machine.current_state, 'enable')
            self.assertEqual(c.hostname, 'R1')
        finally:
            c.disconnect()
            md.stop()

    def test_connect_cat9k_ha_rommon(self):
        md = MockDeviceTcpWrapperIOSXECat9k(hostname='R1', port=0, state='cat9k_ha_active_enable,cat9k_ha_standby_enable')
        md.start()

        c = Connection(
            hostname='switch',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1]),
            ],
            os='iosxe',
            platform='cat9k',
            log_buffer=True,
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             alt=dict(username='admin', password='lab')),
            learn_hostname=True,
        )
        try:
            c.connect()
            c.rommon.timeout = 30
            c.rommon()
        finally:
            c.disconnect()
            md.stop()


class TestIosXECat9kPluginReload(unittest.TestCase):

    def test_reload(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='c9k_login4')
        md.start()

        c = Connection(
            hostname='switch',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            platform='cat9k',
            settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             alt=dict(username='admin', password='lab')),
            mit=True
        )
        try:
            c.connect()
            c.settings.POST_RELOAD_WAIT = 1
            c.reload()
            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()
            md.stop()

    def test_reload_with_error_pattern(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='c9k_login4')
        md.start()

        c = Connection(
            hostname='switch',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            platform='cat9k',
            settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             alt=dict(username='admin', password='lab')),
            mit=True,
        )
        install_add_one_shot_dialog = Dialog([
                Statement(pattern=r"FAILED:.* ",
                          action=None,
                          loop_continue=False,
                          continue_timer=False),
        ])
        error_pattern=[r"FAILED:.* ",]

        try:
            c.connect()
            c.settings.POST_RELOAD_WAIT = 1
            with self.assertRaises(Exception):
                c.reload('active_install_add',
                                reply=install_add_one_shot_dialog,
                                error_pattern = error_pattern)
        finally:
            c.disconnect()
            md.stop()

    def test_reload_with_boot_recovery(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='c9k_login4', hostname='switch')
        md.start()

        testbed = """
        devices:
          R1:
            os: iosxe
            type: cat9k
            credentials:
                default:
                    username: cisco
                    password: cisco
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
            clean:
                device_recovery:
                    golden_image: bootflash:cat9k_iosxe.SSA.bin

        """.format(md.ports[0])

        install_add_one_shot_dialog = Dialog([
                Statement(pattern=r"FAILED:.* ",
                          action=None,
                          loop_continue=False,
                          continue_timer=False),
        ])
        error_pattern=[r"FAILED:.* ",]
        try:
            tb = loader.load(testbed)
            device = tb.devices.R1
            device.api.device_recovery_boot = mock.Mock()
            device.connect()
            with self.assertRaises(Exception):
                device.reload('active_install_add',
                                reply=install_add_one_shot_dialog,
                                error_pattern=error_pattern)
            device.api.device_recovery_boot.assert_called_once_with(golden_image='bootflash:cat9k_iosxe.SSA.bin')
        finally:
            device.disconnect()
            md.stop()


    def test_rommon(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os iosxe --state cat9k_enable_reload_to_rommon'],
                       os='iosxe',
                       platform='cat9k',
                       mit=True,
                       credentials=dict(default=dict(username='cisco', password='cisco'),
                                        alt=dict(username='admin', password='lab')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       log_buffer=True)
        c.connect()
        c.rommon()
        self.assertEqual(c.state_machine.current_state, 'rommon')
        c.disconnect()

    def test_rommon_enable_break(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os iosxe --state cat9k_enable_reload_to_rommon_break'],
                       os='iosxe',
                       platform='cat9k',
                       mit=True,
                       credentials=dict(default=dict(username='cisco', password='cisco'),
                                        alt=dict(username='admin', password='lab')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       log_buffer=True)
        c.connect()
        c.rommon()
        self.assertEqual(c.state_machine.current_state, 'rommon')
        c.disconnect()

    def test_rommon_enable_break2(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os iosxe --state cat9k_enable_reload_to_rommon_break2'],
                       os='iosxe',
                       platform='cat9k',
                       mit=True,
                       credentials=dict(default=dict(username='cisco', password='cisco'),
                                        alt=dict(username='admin', password='lab')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       log_buffer=True)
        c.connect()
        c.rommon()
        self.assertEqual(c.state_machine.current_state, 'rommon')
        c.disconnect()

    def test_rommon_enable_break3(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os iosxe --state cat9k_enable_reload_to_rommon_break3'],
                       os='iosxe',
                       platform='cat9k',
                       mit=True,
                       credentials=dict(default=dict(username='cisco', password='cisco'),
                                        alt=dict(username='admin', password='lab')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       log_buffer=True)
        c.connect()
        c.rommon()
        self.assertEqual(c.state_machine.current_state, 'rommon')
        c.disconnect()

    def test_rommon_enable_break4(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os iosxe --state cat9k_enable_reload_to_rommon_break4'],
                       os='iosxe',
                       platform='cat9k',
                       mit=True,
                       credentials=dict(default=dict(username='cisco', password='cisco'),
                                        alt=dict(username='admin', password='lab')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       log_buffer=True)
        c.connect()
        c.rommon()
        self.assertEqual(c.state_machine.current_state, 'rommon')
        c.disconnect()

    def test_reload_with_image(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os iosxe --state cat9k_enable_reload_to_rommon'],
                       os='iosxe',
                       platform='cat9k',
                       mit=True,
                       credentials=dict(default=dict(username='cisco', password='cisco'),
                                        alt=dict(username='admin', password='lab')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       log_buffer=True)
        c.connect()
        c.settings.POST_RELOAD_WAIT = 1
        c.reload(image_to_boot='tftp://1.1.1.1/latest.bin')
        self.assertEqual(c.state_machine.current_state, 'enable')
        c.disconnect()

    def test_reload_ha(self):
        md = MockDeviceTcpWrapperIOSXECat9k(port=0, state='cat9k_ha_active_escape,cat9k_ha_standby_escape')
        md.start()

        c = Connection(
            hostname='switch',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1]),
            ],
            os='iosxe',
            platform='cat9k',
            settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             alt=dict(username='admin', password='lab')),
            # debug=True
        )
        try:
            c.connect()
            c.settings.POST_RELOAD_WAIT = 1
            c.reload()
            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()
            md.stop()

    def test_connect_ha_from_rommon(self):
        md = MockDeviceTcpWrapperIOSXECat9k(port=0, state='cat9k_ha_active_rommon,cat9k_ha_standby_rommon')
        md.start()

        c = Connection(
            hostname='switch',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1]),
            ],
            os='iosxe',
            platform='cat9k',
            settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             alt=dict(username='admin', password='lab')),
            image_to_boot='tftp://1.1.1.1/latest.bin'
        )
        try:
            c.connect()
            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()
            md.stop()
    """
    def test_reload_ha_from_rommon_with_image(self):
        c = Connection(hostname='switch',
                       start=[
                           'mock_device_cli --os iosxe --state cat9k_ha_active_rommon',
                           'mock_device_cli --os iosxe --state cat9k_ha_standby_rommon'
                        ],
                       os='iosxe',
                       platform='cat9k',
                       credentials=dict(default=dict(username='cisco', password='cisco'),
                                        alt=dict(username='admin', password='lab')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       log_buffer=True)
        try:
            c.connect()
            c.reload(image_to_boot='tftp://1.1.1.1/latest.bin', timeout=60)
            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()
    """
    def test_reload_ha_adding_dialog(self):
        md = MockDeviceTcpWrapperIOSXECat9k(port=0, state='cat9k_ha_active_escape,cat9k_ha_standby_escape')
        md.start()

        c = Connection(
            hostname='switch',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1]),
            ],
            os='iosxe',
            platform='cat9k',
            settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             alt=dict(username='admin', password='lab')),

        )
        install_add_one_shot_dialog = Dialog([
                Statement(pattern=r".*reload of the system\. "
                                  r"Do you want to proceed\? \[y\/n\]",
                          action='sendline(y)',
                          loop_continue=True,
                          continue_timer=False),
            ])
        try:
            c.connect()
            c.settings.POST_RELOAD_WAIT = 1

            c.reload('install add file activate commit',
                               reply=install_add_one_shot_dialog,)
            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()
            md.stop()

    def test_reload_ha_with_error_pattern(self):
        md = MockDeviceTcpWrapperIOSXECat9k(port=0, state='cat9k_ha_active_escape,cat9k_ha_standby_escape')
        md.start()

        c = Connection(
            hostname='switch',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1]),
            ],
            os='iosxe',
            platform='cat9k',
            settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             alt=dict(username='admin', password='lab')),

        )
        install_add_one_shot_dialog = Dialog([
                Statement(pattern=r".*reload of the system\. "
                                  r"Do you want to proceed\? \[y\/n\]",
                          action='sendline(y)',
                          loop_continue=True,
                          continue_timer=False),

                Statement(pattern=r"FAILED:.* ",
                          action=None,
                          loop_continue=False,
                          continue_timer=False),
        ])
        error_pattern=[r"FAILED:.* ",]

        try:
            c.connect()
            c.settings.POST_RELOAD_WAIT = 1
            with self.assertRaises(SubCommandFailure):
                c.reload('install add file activate commit_1',
                                reply=install_add_one_shot_dialog,
                                error_pattern = error_pattern)

            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()
            md.stop()

    def test_reload_ha_with_boot_recovery(self):
        md = MockDeviceTcpWrapperIOSXECat9k(port=0, state='cat9k_ha_active_escape,cat9k_ha_standby_escape', hostname='switch')
        md.start()
        testbed = """
        devices:
          R1:
            os: iosxe
            type: cat9k
            credentials:
                default:
                    username: cisco
                    password: cisco
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {0}
              b:
                protocol: telnet
                ip: 127.0.0.1
                port: {1}
            clean:
                device_recovery:
                    golden_image: bootflash:cat9k_iosxe.SSA.bin

        """.format(md.ports[0],md.ports[1])

        install_add_one_shot_dialog = Dialog([
                Statement(pattern=r".*reload of the system\. "
                                  r"Do you want to proceed\? \[y\/n\]",
                          action='sendline(y)',
                          loop_continue=True,
                          continue_timer=False),

                Statement(pattern=r"FAILED:.* ",
                          action=None,
                          loop_continue=False,
                          continue_timer=False),
        ])
        error_pattern=[r"FAILED:.* ",]
        try:
            tb = loader.load(testbed)
            device = tb.devices.R1
            device.api.device_recovery_boot = mock.Mock()
            device.connect()
            with self.assertRaises(Exception):
                device.reload('install add file activate commit_1',
                                reply=install_add_one_shot_dialog,
                                error_pattern=error_pattern)
            device.api.device_recovery_boot.assert_called_once_with(golden_image='bootflash:cat9k_iosxe.SSA.bin')
        finally:
            device.disconnect()
            md.stop()

    def test_no_boot_system(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state c9k_enable4'],
                       os='iosxe',
                       platform='cat9k',
                       credentials=dict(default=dict(username='admin', password='cisco')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       log_buffer=True
                       )
        d.connect()
        d.settings.CONFIG_LOCK_RETRY_SLEEP = 1
        d.configure("no boot system")
        d.disconnect()

    def test_no_boot_system_1(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state c9k_enable4'],
                       os='iosxe',
                       platform='cat9k',
                       credentials=dict(default=dict(username='admin', password='cisco')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       log_buffer=True
                       )
        d.connect()
        d.settings.CONFIG_LOCK_RETRY_SLEEP = 1
        d.configure(["no boot system",
                     "no boot system"])
        d.disconnect()

    def test_quick_reload(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='c9k_enable')
        md.start()

        c = Connection(
            hostname='switch',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            platform='cat9k',
            settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             alt=dict(username='admin', password='lab')),
            mit=True
        )
        try:
            c.connect()
            c.settings.POST_RELOAD_WAIT = 1
            c.execute('quick reload') # prepare state
            c.reload(timeout=10)
            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()
            md.stop()


class TestIosXeCat9kPluginContainer(unittest.TestCase):

    def test_container_exit(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os iosxe --state meraki_container_shell'],
                       os='iosxe',
                       platform='cat9k',
                       log_buffer=True,
                       init_config_commands=[])
        c.settings.CONTAINER_EXIT_CMDS = ['exit\r', '\x03', '\x03', '\x03']
        c.connect()
        c.disconnect()

    def test_container_ssh(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os iosxe --state meraki_container_ssh'],
                       os='iosxe',
                       platform='cat9k',
                       log_buffer=True,
                       mit=True,
                       init_config_commands=[])
        c.connect()
        c.disconnect()

class TestIosXECat9kEnableSecret(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperIOSXE(port=0, state='enable_secret_password_state')
        cls.md.start()

        cls.testbed = """
        devices:
          Router:
            os: iosxe
            type: router
            credentials:
                default:
                    username: cisco
                    password: cisco
                enable:
                    password: Secret12345
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
        """.format(cls.md.ports[0])
        tb = loader.load(cls.testbed)
        cls.r = tb.devices.Router
        cls.r.connect(init_config_commands=[])

    @classmethod
    def tearDownClass(self):
        self.md.stop()

    def test_reload_enable_secret(self):
        self.r.reload()
        self.r.disconnect()

class TestIosXECat9kGrubConnect(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.device = Connection(
            hostname='switch',
            start=['mock_device_cli --os iosxe --state grub_connect'],
            os='iosxe',
            platform='cat9k',
            log_buffer=True,
            init_config_commands=[],
            credentials=dict(default=dict(username='cisco', password='cisco'))
        )

    @classmethod
    def tearDownClass(cls):
        cls.device.disconnect()

    def test_connect_grub(self):
        self.device.connect()

class TestIosXeCat9kPluginSyslog(unittest.TestCase):

    def test_syslog_messages(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state c9k_enable'],
                       os='iosxe',
                       platform='cat9k',
                       credentials=dict(default=dict(username='admin', password='cisco')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       log_buffer=True
                       )
        try:
            d.connect()
            d.execute('show startup-config', error_pattern=[])
        finally:
            d.disconnect()

class RommonwithConfigRegister(unittest.TestCase):

    def test_rommon_service_transitions_to_rommon(self):
        c = Connection(
            hostname='switch',
            start=['mock_device_cli --os iosxe --state c9800_rommon_boot'],
            os='iosxe',
            platform='cat9k',
            model='c9800',
            mit=True,
            credentials=dict(default=dict(username='cisco', password='cisco')),
            settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
            log_buffer=True
        )
        try:
            c.connect()
            c.rommon() 
            self.assertEqual(c.state_machine.current_state, 'rommon')
        finally:
            c.disconnect()

if __name__ == '__main__':
    unittest.main()
