"""
Unittests for IOSXE/Stack plugin

"""

import re
import unittest
from unittest.mock import MagicMock, Mock, call, patch

from pyats.topology import loader

import unicon
from unicon import Connection
from unicon.eal.dialogs import Statement, Dialog
from unicon.eal.utils import ExpectMatch
from unicon.core.errors import SubCommandFailure
from unicon.plugins.iosxe.stack.service_implementation import StackReload
from unicon.plugins.tests.mock.mock_device_iosxe import MockDeviceTcpWrapperIOSXE
from unicon.plugins.iosxe.stack.utils import StackUtils
from unicon.plugins.generic.service_patterns import reload_patterns
from unicon.plugins.generic.service_statements import reload_statement_list


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

    def test_switchover_with_extended_timeout(self):
        """
        Test switchover with extended timeout to handle device boot sequence.
        """
        # Reset state to ensure clean test
        self.c.active.context.state = None

        # Perform switchover with extended timeout
        self.c.switchover(timeout=1500)

class TestIosXEStackReload(unittest.TestCase):

    class StackReloadPromptSpawn(object):

        def __init__(self, match_index):
            self.timeout = 1
            self.hostname = None
            self.match_index = match_index
            self.match = ExpectMatch()
            self.log = Mock()
            self.sendline = Mock()
            self.match_buffer = Mock(side_effect=self._match_buffer)

        def read_update_buffer(self, size=None):
            return 'Press RETURN to get started!\nUsername:'

        def _match_buffer(self, pat_list):
            self.match.match_output = 'Press RETURN to get started!'
            return self.match_index

        def trim_buffer(self):
            pass

    def test_reload_dialog_matched_retries_reset_for_stack_subconnections(self):
        dialog = Dialog(reload_statement_list)
        press_return_idx, press_return_stmt = next(
            (idx, stmt) for idx, stmt in enumerate(dialog.statements)
            if stmt.pattern == reload_patterns.press_return)
        press_return_stmt.matched_retries = 1
        press_return_stmt.matched_retry_sleep = 0
        press_return_stmt.args = {'wait': 0}

        for _ in range(2):
            spawn = self.StackReloadPromptSpawn(press_return_idx)
            dialog.process(spawn, timeout=1)
            self.assertEqual(spawn.match_buffer.call_count, 2)
            self.assertEqual(spawn.sendline.call_count, 1)

        self.assertEqual(press_return_stmt.matched_retries, 1)

    @patch('unicon.plugins.iosxe.stack.service_implementation.sleep')
    @patch('unicon.plugins.iosxe.stack.service_implementation.utils')
    @patch('unicon.plugins.iosxe.stack.service_implementation.custom_auth_statements',
           return_value=[])
    @patch('unicon.eal.dialogs.Dialog.process')
    def test_stack_reload_post_discovery_return(
            self, mock_process, mock_auth, mock_utils, mock_sleep):
        class Context(dict):
            __getattr__ = dict.__getitem__

        settings = MagicMock(
            STACK_RELOAD_TIMEOUT=10,
            ERROR_PATTERN=[],
            POST_RELOAD_WAIT=0,
            RELOAD_POSTCHECK_INTERVAL=0,
            STACK_POST_RELOAD_SLEEP=0,
            STACK_ROMMON_SLEEP=0,
        )
        connection = MagicMock(settings=settings)
        active = MagicMock(
            alias='peer_1',
            hostname='Router',
            settings=settings,
            context=Context(state='enable'),
        )
        active.spawn = MagicMock()
        connection.active = active
        connection.subconnections = [active]
        mock_utils.is_active_standby_ready.return_value = True

        def run_reload(detected_state=None):
            def dialog_process(*args, **kwargs):
                if mock_process.call_count == 1:
                    if detected_state:
                        kwargs['context']['state'] = detected_state
                    return MagicMock(match_output='discovery')
                return MagicMock(match_output='reload')

            active.context = Context(state='enable')  # stale state
            active.sendline.reset_mock()
            mock_process.reset_mock()
            mock_process.side_effect = dialog_process
            service = StackReload(connection, active.context)
            service.prompt_recovery = False
            service.get_service_result = Mock()
            service.call_service(reload_command='reload')

        # Discovery does not set state, so no post-discovery blank return is
        # sent.
        run_reload()
        active.sendline.assert_called_once_with('reload')
        self.assertNotIn(call(), active.sendline.call_args_list)

        # A state detected by the first dialog still requires the return.
        for state in ('rommon', 'enable', 'disable'):
            with self.subTest(state=state):
                run_reload(state)
                self.assertEqual(active.sendline.call_args_list,
                                 [call('reload'), call()])

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

    
    def test_reload_log_buffer(self):
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

        res, output = d.reload(timeout=10, return_output=True)
        expected_output = ["System configuration has been modified. Save? [yes/no]:", 
                           "Press RETURN to get started!", 
                           "All switches in the stack have been discovered. Accelerating discovery",
                           "The system is not configured to boot automatically",
                           "Reload result: None"]
                
        for expected in expected_output:
            self.assertIn(expected, output)
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


class TestIosXEStackRommon(unittest.TestCase):

    def test_stack_rommon_mixed_states(self):
        """Test StackRommon pre_service with mixed states (rommon and enable)"""
        md = MockDeviceTcpWrapperIOSXE(hostname='Router', port=0,
                                       state='stack_enable,stack_rommon,stack_enable,stack_enable,stack_rommon',
                                       stack=True)
        md.start()
        try:
            con = Connection(hostname='Router',
                           start=['telnet 127.0.0.1 ' + str(i) for i in md.ports[:]],
                           os='iosxe',
                           chassis_type='stack',
                           username='cisco',
                           tacacs_password='cisco',
                           enable_password='cisco',
                           log_buffer=True,
                           debug=True)
            con.settings.STACK_ROMMON_SLEEP = 1
            con.settings.STACK_BOOT_TIMEOUT = 200
            con.connect()
            con.rommon(timeout=20)
            for subcon in con.subconnections:
                self.assertEqual(subcon.state_machine.current_state, 'rommon')

            con.disconnect()
        finally:
            md.stop()


if __name__ == "__main__":
    unittest.main()
