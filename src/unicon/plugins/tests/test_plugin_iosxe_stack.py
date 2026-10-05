"""
Unittests for IOSXE/Stack plugin

"""

import unittest
from unittest.mock import MagicMock, Mock, call, patch

from pyats.topology import loader

import unicon
from unicon import Connection
from unicon.eal.dialogs import Statement, Dialog
from unicon.eal.utils import ExpectMatch
from unicon.core.errors import SubCommandFailure
from unicon.plugins.iosxe.stack.service_implementation import StackReload
from unicon.plugins.iosxe.stack.service_statements import (
    stack_press_return,
    stack_reload_auth_stmt_list,
    stack_wait_and_enter,
)
from unicon.plugins.generic.statements import wait_and_enter as generic_wait_and_enter
from unicon.plugins.tests.mock.mock_device_iosxe import MockDeviceTcpWrapperIOSXE
from unicon.plugins.iosxe.stack.utils import StackUtils
from unicon.plugins.generic.service_patterns import reload_patterns
from unicon.plugins.generic.service_statements import (
    press_enter,
    press_return,
    reload_statement_list,
)


unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0


def get_stack_connection(state, connection_count=5, **kwargs):
    md = MockDeviceTcpWrapperIOSXE(
        hostname='Router', port=0,
        state=','.join([state] * connection_count), stack=True)
    md.start()
    connection = Connection(
        hostname='Router',
        start=['telnet 127.0.0.1 {}'.format(port) for port in md.ports[:]],
        os='iosxe',
        chassis_type='stack',
        **kwargs)
    return md, connection


class TestIosXEStackConnect(unittest.TestCase):

    def test_stack_login_with_short_topologies(self):
        for connection_count in (2, 3):
            with self.subTest(connection_count=connection_count):
                md, connection = get_stack_connection(
                    'stack_login', connection_count=connection_count,
                    credentials={
                        'default': {
                            'username': 'cisco',
                            'password': 'cisco',
                        },
                    })
                try:
                    connection.connect()
                    self.assertEqual(connection.active.alias, 'peer_1')
                    self.assertEqual(connection.standby.alias, 'peer_2')
                    output = connection.execute('show switch')
                    self.assertRegex(output, r'(?m)^\*1\s+Active')
                    self.assertRegex(output, r'(?m)^ 2\s+Standby')
                    self.assertNotRegex(output, r'(?m)^[ *]10\s')
                    if connection_count == 3:
                        self.assertRegex(output, r'(?m)^ 3\s+Member')
                finally:
                    connection.disconnect()
                    md.stop()

    def test_stack_with_six_members_uses_generated_mac(self):
        md, connection = get_stack_connection(
            'stack_enable', connection_count=6)
        try:
            connection.connect()
            output = connection.execute('show switch')
            self.assertRegex(
                output, r'(?m)^ 6\s+Member\s+0200\.0000\.0006')
        finally:
            connection.disconnect()
            md.stop()

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
        md, d = get_stack_connection(
            'stack_login', username='cisco', tacacs_password='cisco',
            enable_password='cisco')
        try:
            d.connect()
            d.execute('term width 0')
            self.assertEqual(d.spawn.match.match_output, 'term width 0\r\nRouter#')
        finally:
            d.disconnect()
            md.stop()

    def test_stack_connect_with_reordered_consoles(self):
        md = MockDeviceTcpWrapperIOSXE(
            hostname='Router', port=0,
            state='stack_enable' + ',stack_enable' * 2, stack=True)
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
            '''.format(md.ports[1], md.ports[0], md.ports[2])
        t = loader.load(testbed)
        d = t.devices.Router
        try:
            d.connect()
            self.assertEqual(d.active.alias, 'p2')
            self.assertEqual(d.standby.alias, 'p1')
            self.assertIs(d._subconnections['p3'], d.p3)

            d.execute('term width 0')
            d.configure('no logging console')
        finally:
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
        cls.md, cls.c = get_stack_connection(
            'stack_enable', username='cisco', tacacs_password='cisco',
            enable_password='cisco')
        cls.c.connect()

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()
        cls.md.stop()

    def test_stack_execute_error_pattern(self):
        with self.assertRaises(SubCommandFailure) as err:
            self.c.execute('not a real command')

    def test_stack_execute(self):
        self.c.execute('show version', target='peer_2')
        self.c.peer_3.execute('show version')


class TestIosXEStackDisableEnable(unittest.TestCase):

    def test_disable_enable(self):
        md, c = get_stack_connection(
            'stack_enable', username='cisco', tacacs_password='cisco',
            enable_password='cisco')
        try:
            c.connect()

            c.disable()
            self.assertEqual(c.spawn.match.match_output, 'disable\r\nRouter>')

            c.enable()
            self.assertEqual(c.spawn.match.match_output, 'cisco\r\nRouter#')

            c.disable(target='standby')
            self.assertEqual(c.standby.spawn.match.match_output, 'disable\r\nRouter>')

            c.enable(target='standby')
            self.assertEqual(c.standby.spawn.match.match_output, 'cisco\r\nRouter#')
        finally:
            c.disconnect()
            md.stop()


class TestIosXEStackConfigure(unittest.TestCase):
    def test_stack_config(self):
        md, c = get_stack_connection(
            'stack_login', username='cisco', tacacs_password='cisco',
            enable_password='cisco', log_buffer=True)
        try:
            c.connect()

            c.configure('no logging console', target='standby')
            c.configure('no logging console', target='peer_3')
            c.peer_1.configure('no logging console')
        finally:
            c.disconnect()
            md.stop()


class TestIosXEStackGetRPState(unittest.TestCase):

    def test_stack_get_rp_state(self):
        md, c = get_stack_connection(
            'stack_login', username='cisco', tacacs_password='cisco',
            enable_password='cisco', log_buffer=True)
        try:
            c.connect()

            r = c.get_rp_state(target='active')
            self.assertEqual(r, 'ACTIVE')

            r = c.get_rp_state(target='standby')
            self.assertEqual(r, 'STANDBY')

            r = c.get_rp_state(target='peer_1')
            self.assertEqual(r, 'MEMBER')
        finally:
            c.disconnect()
            md.stop()


class TestIosXEStackSwitchover(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.md, cls.c = get_stack_connection(
            'stack_login',
            credentials=dict(default=dict(username='cisco', password='cisco')),
            log_buffer=True)
        cls.c.connect()
        cls.c.settings.POST_SWITCHOVER_SLEEP = 1

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()
        cls.md.stop()

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
            self.buffer = 'Press RETURN to get started!'
            self.match = ExpectMatch()
            self.log = Mock()
            self.sendline = Mock()
            self.settings = MagicMock(
                LOGIN_PROMPT=None,
                PASSWORD_PROMPT=None,
            )
            self.match_buffer = Mock(side_effect=self._match_buffer)

        def read_update_buffer(self, size=None):
            return self.buffer

        def _match_buffer(self, pat_list):
            pattern = pat_list[self.match_index]
            self.match.last_match = pattern.search(self.buffer)
            self.match.match_output = self.match.last_match.group()
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

    def test_stack_reload_dialog_uses_stack_press_return(self):
        connection = MagicMock(
            settings=MagicMock(STACK_RELOAD_TIMEOUT=10))
        service = StackReload(connection, {})
        statements = service.dialog.statements

        self.assertEqual(
            sum(statement.action is stack_wait_and_enter
                for statement in statements), 1)
        self.assertFalse(any(
            statement.action is generic_wait_and_enter and
            statement.pattern in (press_enter.pattern, press_return.pattern)
            for statement in statements))

    def test_stack_press_return_sends_return_when_prompt_is_unchanged(self):
        spawn = self.StackReloadPromptSpawn(match_index=0)

        stack_wait_and_enter(spawn, wait=0.01)

        spawn.sendline.assert_called_once_with()

    def test_stack_reload_authenticates_after_press_return(self):
        class StackReloadAuthSpawn:
            def __init__(self):
                self.timeout = 1
                self.hostname = 'Router'
                self.buffer = 'Press RETURN to get started!'
                self.match = ExpectMatch()
                self.log = Mock()
                self.settings = MagicMock(
                    LOGIN_PROMPT=None,
                    PASSWORD_PROMPT=None,
                    PASSWORD_ATTEMPTS=3,
                )
                self.sent_lines = []
                self.last_sent = ''
                self.read_count = 0

            def read_update_buffer(self, size=None):
                self.read_count += 1
                if self.read_count == 2:
                    self.buffer += '\nUsername:'
                return self.buffer

            def match_buffer(self, patterns):
                for index, pattern in enumerate(patterns):
                    match = pattern.search(self.buffer)
                    if match:
                        self.match.last_match = match
                        self.match.match_output = match.group()
                        return index
                raise AssertionError(
                    'No reload dialog pattern matched {!r}'.format(
                        self.buffer))

            def trim_buffer(self):
                self.buffer = self.buffer[self.match.last_match.end():]

            def sendline(self, value=''):
                self.sent_lines.append(value)
                self.last_sent = value
                if value == 'admin':
                    self.buffer += '\nPassword:'
                elif value == 'lab':
                    self.buffer += '\nRouter#'

        spawn = StackReloadAuthSpawn()
        Dialog(stack_reload_auth_stmt_list).process(
            spawn,
            timeout=1,
            context={'username': 'admin', 'tacacs_password': 'lab'})

        self.assertTrue(stack_press_return.loop_continue)
        self.assertEqual(spawn.sent_lines, ['admin', 'lab'])
        self.assertEqual(spawn.buffer, '\nRouter#')
        spawn.log.debug.assert_any_call(
            'Authentication prompt appeared while waiting; skipping RETURN')

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
        cls.md, cls.c = get_stack_connection(
            'stack_login',
            credentials=dict(default=dict(username='cisco', password='cisco')),
            log_buffer=True)
        cls.c.connect()

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()
        cls.md.stop()
    
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
