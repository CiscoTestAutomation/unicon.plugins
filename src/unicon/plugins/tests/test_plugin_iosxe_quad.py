"""
Unittests for IOSXE/Quad plugin

"""

import unittest
from unittest.mock import patch

from pyats.topology import loader

import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure
from unicon.eal.dialogs import Statement, Dialog
from unicon.plugins.tests.mock.mock_device_iosxe import MockDeviceTcpWrapperIOSXE


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestIosXEQuadConnect(unittest.TestCase):

    def test_quad_connect(self):
        md = MockDeviceTcpWrapperIOSXE(hostname='Router',
                                       port=0,
                                       quad=True,
                                       state='quad_login,quad_ics_login,quad_stby_login,quad_ics_login')
        md.start()
        d = Connection(hostname='Router',
                       start=['telnet 127.0.0.1 ' + str(i) for i in md.ports[:]],
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
                       start=['mock_device_cli --os iosxe --state quad_login --hostname Router',
                              'mock_device_cli --os iosxe --state quad_ics_login --hostname Router',
                              'mock_device_cli --os iosxe --state quad_stby_login --hostname Router',
                              'mock_device_cli --os iosxe --state quad_ics_login --hostname Router'],
                       os='iosxe',
                       chassis_type='quad',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        d.connect()
        d.execute('term width 0')
        self.assertEqual(d.spawn.match.match_output, 'term width 0\r\nRouter#')
        d.disconnect()

    def test_quad_connect3(self):
        md = MockDeviceTcpWrapperIOSXE(hostname='Router',
                                       port=0,
                                       quad=True,
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
                       start=['mock_device_cli --os iosxe --state quad_login --hostname Router',
                              'mock_device_cli --os iosxe --state quad_ics_login --hostname Router',
                              'mock_device_cli --os iosxe --state quad_stby_login --hostname Router',
                              'mock_device_cli --os iosxe --state quad_ics_login --hostname Router'],
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

        d.disconnect()


class TestIosXEQuadGetRPState(unittest.TestCase):

    def test_get_rp_state(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state quad_login --hostname Router',
                              'mock_device_cli --os iosxe --state quad_ics_login --hostname Router',
                              'mock_device_cli --os iosxe --state quad_stby_login --hostname Router',
                              'mock_device_cli --os iosxe --state quad_ics_login --hostname Router'],
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

        d.disconnect()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestIosXEQuadSwitchover(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperIOSXE(hostname='Router',
                                           port=0,
                                           quad=True,
                                           state='quad_login,quad_ics_login,quad_stby_login,quad_ics_login')
        cls.md.start()

        cls.d = Connection(hostname='Router',
                           start=['telnet 127.0.0.1 ' + str(i) for i in cls.md.ports[:]],
                           os='iosxe',
                           chassis_type='quad',
                           username='cisco',
                           tacacs_password='cisco',
                           enable_password='cisco')
        cls.d.connect()

    @classmethod
    def tearDownClass(cls):
        cls.d.disconnect()
        cls.md.stop()

    def test_reload(self):
        self.d.switchover()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestIosXEQuadReload(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperIOSXE(hostname='Router',
                                           port=0,
                                           quad=True,
                                           state='quad_login,quad_ics_login,quad_stby_login,quad_ics_login')
        cls.md.start()

        cls.d = Connection(hostname='Router',
                           start=['telnet 127.0.0.1 ' + str(i) for i in cls.md.ports[:]],
                           os='iosxe',
                           chassis_type='quad',
                           username='cisco',
                           tacacs_password='cisco',
                           enable_password='cisco')
        cls.d.settings.QUAD_RELOAD_SLEEP = 0
        cls.d.connect()

    @classmethod
    def tearDownClass(cls):
        cls.d.disconnect()
        cls.md.stop()

    def test_reload(self):
        self.d.reload()

    def test_reload_with_error_pattern(self):

        install_add_one_shot_dialog = Dialog([
                Statement(pattern=r"FAILED:.* ",
                          action=None,
                          loop_continue=False,
                          continue_timer=False),
         ])
        error_pattern=[r"FAILED:.* ",]

        with self.assertRaises(SubCommandFailure):
                self.d.reload('active_install_add',
                          reply=install_add_one_shot_dialog,
                          error_pattern = error_pattern)
        self.assertEqual(self.d.reload.error_pattern, error_pattern)

if __name__ == "__main__":
    unittest.main()
