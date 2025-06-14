"""
Unittests for IOSXE/Stack plugin

"""

import re
import unittest
from unittest.mock import Mock, patch

from pyats.topology import loader

import unicon
from unicon import Connection
from unicon.eal.dialogs import Statement, Dialog
from unicon.core.errors import SubCommandFailure
from unicon.plugins.tests.mock.mock_device_iosxe import MockDeviceTcpWrapperIOSXE
from unicon.plugins.iosxe.stack.utils import StackUtils


unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0


class TestIosXEStackConnect(unittest.TestCase):

    def test_stack_connect(self):
        md = MockDeviceTcpWrapperIOSXE(hostname='Router', port=0, state='stack_login' + ',stack_login'*4, stack=True)
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
                       start = ['mock_device_cli --os iosxe --state stack_login --hostname Router']*5,
                       os='iosxe',
                       chassis_type='stack',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        d.connect()
        d.execute('term width 0')
        self.assertEqual(d.spawn.match.match_output, 'term width 0\r\nRouter#')

    def test_stack_connect3(self):
        md = MockDeviceTcpWrapperIOSXE(hostname='Router', port=0, state='stack_enable' + ',stack_enable'*2, stack=True)
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

    def test_stack_connect4(self):
        md = MockDeviceTcpWrapperIOSXE(hostname='Router', port=0, state='stack_rommon' + ',stack_rommon'*4, stack=True)
        md.start()
        d = Connection(hostname='Router',
                       start = ['telnet 127.0.0.1 ' + str(i) for i in md.ports[:]],
                       os='iosxe',
                       chassis_type='stack',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       )
        d.connect()
        self.assertTrue(d.active.alias == 'peer_1')
        d.disconnect()
        md.stop()


class TestIosXEStackExecute(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                       start = ['mock_device_cli --os iosxe --state stack_enable --hostname Router']*5,
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
                       start = ['mock_device_cli --os iosxe --state stack_enable --hostname Router']*5,
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
                       start = ['mock_device_cli --os iosxe --state stack_login --hostname Router']*5,
                       os='iosxe',
                       chassis_type='stack',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco',
                       log_buffer=True)
        c.connect()

        c.configure('no logging console', target='standby')
        c.configure('no logging console', target='peer_3')
        c.peer_1.configure('no logging console')


class TestIosXEStackGetRPState(unittest.TestCase):

    def test_stack_get_rp_state(self):
        c = Connection(hostname='Router',
                       start = ['mock_device_cli --os iosxe --state stack_login --hostname Router']*5,
                       os='iosxe',
                       chassis_type='stack',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco',
                       log_buffer=True)
        c.connect()

        r = c.get_rp_state(target='active')
        self.assertEqual(r, 'ACTIVE')

        r = c.get_rp_state(target='standby')
        self.assertEqual(r, 'STANDBY')

        r = c.get_rp_state(target='peer_1')
        self.assertEqual(r, 'MEMBER')


class TestIosXEStackSwitchover(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                           start = ['mock_device_cli --os iosxe --state stack_login --hostname Router']*5,
                           os='iosxe',
                           chassis_type='stack',
                           credentials=dict(default=dict(username='cisco', password='cisco')),
                           log_buffer=True)
        cls.c.connect()
        cls.c.settings.POST_SWITCHOVER_SLEEP = 1

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()

    def test_switchover(self):
        self.c.active.context.state = None
        self.c.switchover()

    def test_switchover_context(self):
        # explicitly set the context.state to hit the codepath with context
        self.c.active.context.state = 'rommon'
        self.c.switchover()


class TestIosXEStackReload(unittest.TestCase):

    def test_reload(self):
        md = MockDeviceTcpWrapperIOSXE(hostname='Router', port=0, state='stack_enable' + ',stack_enable'*4, stack=True)
        md.start()
        d = Connection(hostname='Router',
                       start = ['telnet 127.0.0.1 ' + str(i) for i in md.ports[:]],
                       os='iosxe',
                       chassis_type='stack',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        d.settings.STACK_POST_RELOAD_SLEEP = 0
        d.settings.STACK_ROMMON_SLEEP = 1
        d.settings.POST_RELOAD_WAIT = 1
        d.connect()
        self.assertTrue(d.active.alias == 'peer_1')

        d.reload(timeout=10)
        d.disconnect()
        md.stop()

    def test_reload_member(self):

        md = MockDeviceTcpWrapperIOSXE(port=0, state='stack_enable' + ',stack_enable'*4, stack=True)
        md.start()
        d = Connection(hostname='Router',
                       start = ['telnet 127.0.0.1 ' + str(i) for i in md.ports[:]],
                       os='iosxe',
                       chassis_type='stack',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        d.settings.STACK_POST_RELOAD_SLEEP = 0
        d.settings.STACK_ROMMON_SLEEP = 1
        d.settings.POST_RELOAD_WAIT = 1
        d.connect()
        self.assertTrue(d.active.alias == 'peer_1')

        d.reload(member=1, timeout=10)
        d.disconnect()
        md.stop()

    def test_reload_with_error_pattern(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='stack_enable' + ',stack_enable'*4, stack=True)
        md.start()
        d = Connection(hostname='Router',
                       start = ['telnet 127.0.0.1 ' + str(i) for i in md.ports[:]],
                       os='iosxe',
                       chassis_type='stack',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')

        install_add_one_shot_dialog = Dialog([
                Statement(pattern=r"FAILED:.* ",
                          action=None,
                          loop_continue=False,
                          continue_timer=False),
         ])
        error_pattern=[r"FAILED:.* ",]

        try:
            d.connect()
            d.settings.STACK_POST_RELOAD_SLEEP = 0
            d.settings.STACK_ROMMON_SLEEP = 1
            d.settings.POST_RELOAD_WAIT = 1
            with self.assertRaises(SubCommandFailure):
                d.reload('active_install_add',
                          reply=install_add_one_shot_dialog,
                          error_pattern = error_pattern,
                          timeout=10)
            self.assertEqual(d.reload.error_pattern, error_pattern)
        finally:
             d.disconnect()
             md.stop()

    def test_reload_member_with_post_reload_wait_time(self):

        md = MockDeviceTcpWrapperIOSXE(port=0, state='stack_enable' + ',stack_enable'*4, stack=True)
        md.start()
        d = Connection(hostname='Router',
                       start = ['telnet 127.0.0.1 ' + str(i) for i in md.ports[:]],
                       os='iosxe',
                       chassis_type='stack',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco',
                       post_reload_wait_time='120')
        d.settings.STACK_POST_RELOAD_SLEEP = 0
        d.settings.STACK_ROMMON_SLEEP = 1
        d.settings.POST_RELOAD_WAIT = 1
        d.connect()
        self.assertTrue(d.active.alias == 'peer_1')

        d.reload(member=1, timeout=10)
        d.disconnect()
        md.stop()


class TestIosXEluginBashService(unittest.TestCase):

    def test_bash(self):
        md = MockDeviceTcpWrapperIOSXE(hostname='Router', port=0, state='stack_enable' + ',stack_enable'*4, stack=True)
        md.start()
        try:
            d = Connection(hostname='Router',
                        start = ['telnet 127.0.0.1 ' + str(i) for i in md.ports[:]],
                        os='iosxe',
                        chassis_type='stack',
                        username='cisco',
                        tacacs_password='cisco',
                        enable_password='cisco')
            d.connect()
            with d.bash_console() as console:
                console.execute('df /bootflash/')
            self.assertIn('exit', d.spawn.match.match_output)
            self.assertIn('Router#', d.spawn.match.match_output)
            d.disconnect()
        finally:
            md.stop()


class TestIosXEStackUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                           start = ['mock_device_cli --os iosxe --state stack_login --hostname Router']*5,
                           os='iosxe',
                           chassis_type='stack',
                           credentials=dict(default=dict(username='cisco', password='cisco')),
                           log_buffer=True)
        cls.c.connect()
    
    def test_get_redundancy_details(self):
        su = StackUtils()
        rd = su.get_redundancy_details(connection=self.c)
        self.assertDictEqual({
                                "1": {
                                    "sw_num": "1",
                                    "role": "Member",
                                    "mac": "bcc4.9346.7880",
                                    "state": "Ready"
                                },
                                "2": {
                                    "sw_num": "2",
                                    "role": "Active",
                                    "mac": "bcc4.9346.9180",
                                    "state": "Ready"
                                },
                                "3": {
                                    "sw_num": "3",
                                    "role": "Member",
                                    "mac": "bcc4.9346.7a00",
                                    "state": "Ready"
                                },
                                "4": {
                                    "sw_num": "4",
                                    "role": "Standby",
                                    "mac": "bcc4.9346.6780",
                                    "state": "Ready"
                                },
                                "5": {
                                    "sw_num": "5",
                                    "role": "Member",
                                    "mac": "bcc4.9346.7280",
                                    "state": "Ready"
                                },
                                "10": {
                                    "sw_num": "10",
                                    "role": "Standby",
                                    "mac": "e069.ba68.5900",
                                    "state": "Ready"
                                }
                            }, rd)


if __name__ == "__main__":
    unittest.main()
