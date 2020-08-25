"""
Unittests for IOSXE/Stack plugin

"""

import re
import unittest
from unittest.mock import Mock, patch

from pyats.topology import loader

import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure
from unicon.plugins.tests.mock.mock_device_iosxe import MockDeviceTcpWrapperIOSXE


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestIosXEStackConnect(unittest.TestCase):

    def test_stack_connect(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='stack_login' + ',stack_login'*4, stack=True)
        md.start()
        d = Connection(hostname='Router',
                       start = ['telnet 127.0.0.1 ' + str(i) for i in md.ports[:]],
                       os='iosxe',
                       chassis_type='stack',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        d.connect()
        self.assertTrue(d.active.alias == 'peer_2')

        d.execute('term width 0')
        d.configure('no logging console')
        d.disconnect()
        md.stop()

    def test_stack_connect2(self):
        d = Connection(hostname='Router',
                       start = ['mock_device_cli --os iosxe --state stack_login']*5,
                       os='iosxe',
                       chassis_type='stack',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        d.connect()
        d.execute('term width 0')
        self.assertEqual(d.spawn.match.match_output, 'term width 0\r\nRouter#')

    def test_stack_connect3(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='stack_enable' + ',stack_enable'*2, stack=True)
        md.start()
        testbed = '''
            devices:
              Router:
                type: router
                os: iosxe
                chassis_type: stack
                connections:
                  defaults:
                    class: 'unicon.Unicon'
                    connections: [p1, p2, p3]
                  p1:
                    protocol: telnet
                    ip: 127.0.0.1
                    port: {}
                  p2:
                    protocol: telnet
                    ip: 127.0.0.1
                    port: {}
                  p3:
                    protocol: telnet
                    ip: 127.0.0.1
                    port: {}
            '''.format(md.ports[0], md.ports[1], md.ports[2])
        t = loader.load(testbed)
        d = t.devices.Router
        d.connect()
        self.assertTrue(d.active.alias == 'p1')

        d.execute('term width 0')
        d.configure('no logging console')
        d.disconnect()
        md.stop()


class TestIosXEStackExecute(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                       start = ['mock_device_cli --os iosxe --state stack_enable']*5,
                       os='iosxe',
                       chassis_type='stack',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        cls.c.connect()

    def test_stack_execute_error_pattern(self):
        with self.assertRaises(SubCommandFailure) as err:
            self.c.execute('not a real command')

    def test_stack_execute(self):
        self.c.execute('show version', target='peer_2')
        self.c.peer_3.execute('show version')


class TestIosXEStackDisableEnable(unittest.TestCase):

    def test_disable_enable(self):
        c = Connection(hostname='Router',
                       start = ['mock_device_cli --os iosxe --state stack_enable']*5,
                       os='iosxe',
                       chassis_type='stack',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        c.connect()

        r = c.disable()
        self.assertEqual(c.spawn.match.match_output, 'disable\r\nRouter>')

        r = c.enable()
        self.assertEqual(c.spawn.match.match_output, 'cisco\r\nRouter#')

        r = c.disable(target='standby')
        self.assertEqual(c.standby.spawn.match.match_output, 'disable\r\nRouter>')

        r = c.enable(target='standby')
        self.assertEqual(c.standby.spawn.match.match_output, 'cisco\r\nRouter#')


class TestIosXEStackConfigure(unittest.TestCase):
    def test_stack_config(self):
        c = Connection(hostname='Router',
                       start = ['mock_device_cli --os iosxe --state stack_login']*5,
                       os='iosxe',
                       chassis_type='stack',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        c.connect()

        c.configure('no logging console', target='standby')
        c.configure('no logging console', target='peer_3')
        c.peer_1.configure('no logging console')


class TestIosXEStackGetRPState(unittest.TestCase):

    def test_stack_get_rp_state(self):
        c = Connection(hostname='Router',
                       start = ['mock_device_cli --os iosxe --state stack_login']*5,
                       os='iosxe',
                       chassis_type='stack',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        c.connect()

        r = c.get_rp_state(target='active')
        self.assertEqual(r, 'ACTIVE')

        r = c.get_rp_state(target='standby')
        self.assertEqual(r, 'STANDBY')

        r = c.get_rp_state(target='peer_1')
        self.assertEqual(r, 'MEMBER')


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestIosXEStackSwitchover(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                       start = ['mock_device_cli --os iosxe --state stack_login']*5,
                       os='iosxe',
                       chassis_type='stack',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        cls.c.connect()

    def test_reload(self):
        self.c.switchover()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestIosXEStackReload(unittest.TestCase):

    def test_reload(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='stack_enable' + ',stack_enable'*4, stack=True)
        md.start()
        d = Connection(hostname='Router',
                       start = ['telnet 127.0.0.1 ' + str(i) for i in md.ports[:]],
                       os='iosxe',
                       chassis_type='stack',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        d.connect()
        self.assertTrue(d.active.alias == 'peer_1')

        d.reload()
        md.stop()


if __name__ == "__main__":
    unittest.main()
