"""
Unittests for IOSXE/Quad plugin

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
class TestIosXEQuadConnect(unittest.TestCase):

    def test_quad_connect(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, quad=True,
                state='quad_login,quad_ics_login,quad_stby_login,quad_ics_login')
        md.start()
        d = Connection(hostname='Router',
                       start = ['telnet 127.0.0.1 ' + str(i) for i in md.ports[:]],
                       os='iosxe',
                       chassis_type='quad',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        d.connect()
        self.assertTrue(d.active.alias == 'a')
        d.disconnect()
        md.stop()

    def test_quad_connect2(self):
        d = Connection(hostname='Router',
                       start = ['mock_device_cli --os iosxe --state quad_login',
                                'mock_device_cli --os iosxe --state quad_ics_login',
                                'mock_device_cli --os iosxe --state quad_stby_login',
                                'mock_device_cli --os iosxe --state quad_ics_login',],
                       os='iosxe',
                       chassis_type='quad',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        d.connect()
        d.execute('term width 0')
        self.assertEqual(d.spawn.match.match_output, 'term width 0\r\nRouter#')

    def test_quad_connect3(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, quad=True,
                state='quad_login,quad_ics_login,quad_stby_login,quad_ics_login')
        md.start()
        testbed = '''
            devices:
              Router:
                type: router
                os: iosxe
                chassis_type: quad
                credentials:
                  default:
                    password: cisco
                    username: cisco
                  enable:
                    password: cisco
                    username: cisco
                connections:
                  defaults:
                    class: 'unicon.Unicon'
                    connections: [a, b, c, d]
                  a:
                    protocol: telnet
                    ip: 127.0.0.1
                    port: {}
                    member: 1
                  b:
                    protocol: telnet
                    ip: 127.0.0.1
                    port: {}
                    member: 1
                  c:
                    protocol: telnet
                    ip: 127.0.0.1
                    port: {}
                    member: 2
                  d:
                    protocol: telnet
                    ip: 127.0.0.1
                    port: {}
                    member: 2
            '''.format(md.ports[0], md.ports[1], md.ports[2], md.ports[3])

        t = loader.load(testbed)
        d = t.devices.Router
        d.connect()
        self.assertTrue(d.active.alias == 'a')

        d.execute('term width 0')
        d.configure('no logging console')
        d.disconnect()
        md.stop()


class TestIosXEQuadDisableEnable(unittest.TestCase):

    def test_disable_enable(self):
        d = Connection(hostname='Router',
                       start = ['mock_device_cli --os iosxe --state quad_login',
                                'mock_device_cli --os iosxe --state quad_ics_login',
                                'mock_device_cli --os iosxe --state quad_stby_login',
                                'mock_device_cli --os iosxe --state quad_ics_login',],
                       os='iosxe',
                       chassis_type='quad',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        d.connect()

        d.disable()
        self.assertEqual(d.spawn.match.match_output, 'disable\r\nRouter>')

        d.enable()
        self.assertEqual(d.spawn.match.match_output, 'cisco\r\nRouter#')

        d.disable(target='standby')
        self.assertEqual(d.standby.spawn.match.match_output, 'disable\r\nRouter-stby>')

        d.enable(target='standby')
        self.assertEqual(d.standby.spawn.match.match_output, 'cisco\r\nRouter-stby#')


class TestIosXEQuadGetRPState(unittest.TestCase):

    def test_get_rp_state(self):
        d = Connection(hostname='Router',
                       start = ['mock_device_cli --os iosxe --state quad_login',
                                'mock_device_cli --os iosxe --state quad_ics_login',
                                'mock_device_cli --os iosxe --state quad_stby_login',
                                'mock_device_cli --os iosxe --state quad_ics_login',],
                       os='iosxe',
                       chassis_type='quad',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        d.connect()

        r = d.get_rp_state(target='active')
        self.assertEqual(r, 'ACTIVE')

        r = d.get_rp_state(target='standby')
        self.assertEqual(r, 'STANDBY')

        r = d.get_rp_state(target='b')
        self.assertEqual(r, 'IN_CHASSIS_STANDBY')


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestIosXEQuadSwitchover(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperIOSXE(port=0, quad=True,
                state='quad_login,quad_ics_login,quad_stby_login,quad_ics_login')
        cls.md.start()

        cls.d = Connection(hostname='Router',
                    start = ['telnet 127.0.0.1 ' + str(i) for i in cls.md.ports[:]],
                    os='iosxe',
                    chassis_type='quad',
                    username='cisco',
                    tacacs_password='cisco',
                    enable_password='cisco')
        cls.d.connect()

    @classmethod
    def tearDownClass(cls):
        cls.md.stop()

    def test_reload(self):
        self.d.switchover()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestIosXEQuadReload(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperIOSXE(port=0, quad=True,
                state='quad_login,quad_ics_login,quad_stby_login,quad_ics_login')
        cls.md.start()

        cls.d = Connection(hostname='Router',
                    start = ['telnet 127.0.0.1 ' + str(i) for i in cls.md.ports[:]],
                    os='iosxe',
                    chassis_type='quad',
                    username='cisco',
                    tacacs_password='cisco',
                    enable_password='cisco')
        cls.d.connect()

    @classmethod
    def tearDownClass(cls):
        cls.md.stop()

    def test_reload(self):
        self.d.reload()


if __name__ == "__main__":
    unittest.main()
