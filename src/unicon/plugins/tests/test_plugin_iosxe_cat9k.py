"""
Unittests for iosxe/cat9k plugin
"""

import unittest

import unicon
from unicon import Connection
from unicon.plugins.tests.mock.mock_device_iosxe import MockDeviceTcpWrapperIOSXE
from unicon.plugins.tests.mock.mock_device_iosxe_cat9k import MockDeviceTcpWrapperIOSXECat9k


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


class TestIosXeCat9kPluginContainer(unittest.TestCase):

    def test_container_exit(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os iosxe --state meraki_container_shell'],
                       os='iosxe',
                       platform='cat9k',
                       log_buffer=True,
                       init_config_commands=[])
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


if __name__ == '__main__':
    unittest.main()
