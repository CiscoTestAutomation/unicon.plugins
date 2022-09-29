"""
Unittests for iosxe/cat8k plugin
"""

import unittest

import unicon
from unicon import Connection
from unicon.plugins.tests.mock.mock_device_iosxe_cat8k import MockDeviceTcpWrapperIOSXECat8k
from unicon.core.errors import SubCommandFailure


unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXeCat8kPlugin(unittest.TestCase):

    def test_connect(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state c8k_login'],
                       os='iosxe',
                       platform='cat8k',
                       credentials=dict(default=dict(username='admin', password='cisco')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       log_buffer=True
                       )
        d.connect()
        d.disconnect()

    def test_connect_learn_hostname(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state c8k_login --hostname WLC'],
                       os='iosxe',
                       platform='cat8k',
                       credentials=dict(default=dict(username='admin', password='cisco')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       learn_hostname=True,
                       log_buffer=True
                       )
        d.connect()
        d.disconnect()



class TestIosXECat8kPluginSwitchover(unittest.TestCase):

    def test_switchover(self):
        md = MockDeviceTcpWrapperIOSXECat8k(port=0, state='c8k_login')
        md.start()

        c = Connection(
            hostname='Switch',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            platform='cat8k',
            settings=dict(
                POST_DISCONNECT_WAIT_SEC=0,
                GRACEFUL_DISCONNECT_WAIT_SEC=0.2,
                POST_HA_RELOAD_CONFIG_SYNC_WAIT=1,
                POST_SWITCHOVER_WAIT=1,
            ),
            credentials=dict(default=dict(username='admin', password='cisco')),
            mit=True,
        )
        try:
            c.connect()
            c.switchover()
            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()
            md.stop()

    def test_switchover_output(self):
        md = MockDeviceTcpWrapperIOSXECat8k(port=0, state='c8k_login')
        md.start()

        c = Connection(
            hostname='Switch',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            platform='cat8k',
            settings=dict(
                POST_DISCONNECT_WAIT_SEC=0,
                GRACEFUL_DISCONNECT_WAIT_SEC=0.2,
                POST_HA_RELOAD_CONFIG_SYNC_WAIT=1,
                POST_SWITCHOVER_WAIT=1,
            ),
            credentials=dict(default=dict(username='admin', password='cisco')),
            mit=True,
        )
        try:
            c.connect()
            status = c.switchover(return_output=True)
            self.assertTrue(status.result)
            self.assertIn(
                'IOSXE_INFRA-6-CONSOLE_ACTIVE: R0/1 console active.',
                status.output)
        finally:
            c.disconnect()
            md.stop()

    def test_switchover_failure_device_not_in_HA_mode(self):
        md = MockDeviceTcpWrapperIOSXECat8k(port=0, state='c8k_login2')
        md.start()

        c = Connection(
            hostname='Switch',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            platform='cat8k',
            settings=dict(
                POST_DISCONNECT_WAIT_SEC=0,
                GRACEFUL_DISCONNECT_WAIT_SEC=0.2,
                POST_SWITCHOVER_WAIT=1,
            ),
            credentials=dict(default=dict(username='admin', password='cisco')),
            mit=True,
        )
        try:
            c.connect()
            with self.assertRaises(SubCommandFailure):
                c.switchover()
        finally:
            c.disconnect()
            md.stop()

    def test_switchover_failure_standby_sync_timeout(self):
        md = MockDeviceTcpWrapperIOSXECat8k(port=0, state='c8k_login3')
        md.start()

        c = Connection(
            hostname='Switch',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            platform='cat8k',
            settings=dict(
                POST_DISCONNECT_WAIT_SEC=0,
                GRACEFUL_DISCONNECT_WAIT_SEC=0.2,
                POST_HA_RELOAD_CONFIG_SYNC_WAIT=1,
                SWITCHOVER_COUNTER=2,
                POST_SWITCHOVER_WAIT=1,
                ),
            credentials=dict(default=dict(username='admin', password='cisco')),
            mit=True,
        )
        try:
            c.connect()
            self.assertFalse(c.switchover())
        finally:
            c.disconnect()
            md.stop()
class TestIosXECat8kPluginReload(unittest.TestCase):

    def test_reload_with_image(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os iosxe --state cat8k_enable_reload_to_rommon'],
                       os='iosxe',
                       platform='cat8k',
                       mit=True,
                       credentials=dict(default=dict(username='admin', password='cisco')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       log_buffer=True)
        c.connect()
        c.settings.POST_RELOAD_WAIT = 1
        c.reload(image_to_boot='tftp://1.1.1.1/latest.bin', timeout=10)
        self.assertEqual(c.state_machine.current_state, 'enable')
        c.disconnect()

if __name__ == '__main__':
    unittest.main()
