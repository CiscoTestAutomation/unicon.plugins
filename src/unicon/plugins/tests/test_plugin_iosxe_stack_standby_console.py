"""
Unittests for the IOSXE/Stack standby console attach.

On a C9300 stack every member console presents the active RP's CLI, so the
handle unicon designates as standby is really a second session on the active.
These tests cover the detection and the attach that corrects it.

The existing stack tests start several *identical* mock devices, so they cannot
express "console A is active and console B is standby". The logic is therefore
driven directly here.
"""

import unittest
from unittest.mock import MagicMock, patch

from unicon.plugins.iosxe.stack.connection_provider import (
    CONSOLE_BANNER_PATTERN,
    CONSOLE_BUSY_PATTERN,
    SHOW_SWITCH_ROW_RE,
    StackRpConnectionProvider,
    _console_banner_handler,
    _console_busy_handler,
)

import re


SHOW_SWITCH_ACTIVE = """show switch
Switch/Stack Mac Address : 74e2.e72d.8180 - Local Mac Address
Mac persistency wait time: Indefinite
                                             H/W   Current
Switch#   Role    Mac Address     Priority Version  State
-------------------------------------------------------------------------------
*1       Active   74e2.e72d.8180     1      V07     Ready
 2       Member   c4ab.4d73.eb80     1      V07     Ready
 3       Standby  74e2.e72d.9080     1      V07     Ready
Switch#"""

SHOW_SWITCH_STANDBY = SHOW_SWITCH_ACTIVE.replace(
    '*1       Active', ' 1       Active').replace(
    ' 3       Standby', '*3       Standby')

ATTACH_BANNER = (
    'request platform software console attach switch standby R0\r\n'
    '#\r\n'
    '# Connecting to the IOS console on the route-processor in slot 0.\r\n'
    '# Enter Control-C to exit.\r\n'
    '#\r\n'
)

BUSY_OUTPUT = ('request platform software console attach switch standby R0\r\n'
               '#ioucon:TTY open (remote): Address already in use\r\n')


def make_provider(connection):
    """Build the provider without running the real __init__."""
    provider = StackRpConnectionProvider.__new__(StackRpConnectionProvider)
    provider.connection = connection
    provider.prompt_recovery = False
    return provider


def make_subcon(output, alias='peer_1'):
    subcon = MagicMock()
    subcon.alias = alias
    subcon.execute.return_value = output
    subcon.context = {}
    return subcon


class TestShowSwitchParsing(unittest.TestCase):
    """The '*' row identifies the console; the standby need not be switch 2."""

    def _local(self, output):
        provider = make_provider(MagicMock())
        return provider._get_local_switch(make_subcon(output))

    def test_active_console(self):
        self.assertEqual(self._local(SHOW_SWITCH_ACTIVE), ('1', 'Active'))

    def test_standby_console_is_switch_3(self):
        self.assertEqual(self._local(SHOW_SWITCH_STANDBY), ('3', 'Standby'))

    def test_ignores_non_local_rows(self):
        """Switch 3 is Standby but is not this console."""
        self.assertEqual(self._local(SHOW_SWITCH_ACTIVE)[1], 'Active')

    def test_no_star_row(self):
        self.assertEqual(self._local('show switch\nSwitch#'), (None, None))

    def test_multi_digit_switch_number(self):
        output = '*12      Standby  74e2.e72d.9080     1      V07     Ready'
        self.assertEqual(self._local(output), ('12', 'Standby'))

    def test_execute_failure(self):
        provider = make_provider(MagicMock())
        subcon = MagicMock()
        subcon.execute.side_effect = Exception('boom')
        self.assertEqual(provider._get_local_switch(subcon), (None, None))


class TestConsolePatterns(unittest.TestCase):

    def test_busy_pattern_matches_device_message(self):
        self.assertTrue(re.match(CONSOLE_BUSY_PATTERN,
                                 '#ioucon:TTY open (remote): Address already in use'))

    def test_busy_pattern_ignores_normal_banner(self):
        self.assertIsNone(re.match(CONSOLE_BUSY_PATTERN,
                                   '# Enter Control-C to exit.'))

    def test_banner_pattern_matches(self):
        self.assertTrue(re.match(CONSOLE_BANNER_PATTERN,
                                 '# Enter Control-C to exit.'))

    def test_busy_handler_flags_context(self):
        context = {}
        _console_busy_handler(MagicMock(), context)
        self.assertTrue(context['_standby_console_busy'])

    def test_banner_handler_pokes_console(self):
        """The attached console prints nothing until it receives a newline."""
        spawn = MagicMock()
        _console_banner_handler(spawn, {})
        spawn.sendline.assert_called_once_with()


class TestAttachPokesUntilPrompt(unittest.TestCase):
    """A poke sent before the console is ready is swallowed, so it must retry."""

    def _provider(self):
        con = MagicMock()
        con.settings.STACK_STANDBY_CONSOLE_PLANE = 'R0'
        con.settings.STACK_STANDBY_CONSOLE_ATTACH_TIMEOUT = 10
        con.settings.STACK_STANDBY_CONSOLE_POLL_INTERVAL = 1
        # Real Statement objects are built from these, so they must be strings.
        con.settings.LOGIN_PROMPT = r'^.*[Uu]sername: ?$'
        con.settings.PASSWORD_PROMPT = r'^.*[Pp]assword: ?$'
        provider = make_provider(con)
        return provider

    def _subcon(self):
        subcon = MagicMock()
        subcon.context = {}
        subcon.hostname = 'CTS-REG-UUT1'
        # MagicMock auto-creates attributes, so start from a real False.
        subcon._standby_console_attached = False
        return subcon

    def test_retries_poke_when_console_stays_silent(self):
        provider = self._provider()
        subcon = self._subcon()

        # Silent twice, then the prompt arrives.
        attempts = [TimeoutError('timeout'), TimeoutError('timeout'), None]

        def process(*args, **kwargs):
            outcome = attempts.pop(0)
            if outcome:
                raise outcome

        with patch('unicon.plugins.iosxe.stack.connection_provider.Dialog') as dialog:
            dialog.return_value.process.side_effect = process
            provider._attach_standby_console(subcon)

        self.assertEqual(dialog.return_value.process.call_count, 3)
        self.assertGreaterEqual(subcon.spawn.sendline.call_count, 2)

    def test_prompt_recovery_disabled_during_attach(self):
        """Prompt recovery sends Ctrl-C, which would exit the attach."""
        provider = self._provider()
        # Enabled on the provider, so passing it through would be visible here.
        provider.prompt_recovery = True
        subcon = self._subcon()

        with patch('unicon.plugins.iosxe.stack.connection_provider.Dialog') as dialog:
            provider._attach_standby_console(subcon)

        _, kwargs = dialog.return_value.process.call_args
        self.assertFalse(kwargs['prompt_recovery'])

    def test_busy_stops_retrying_immediately(self):
        provider = self._provider()
        subcon = self._subcon()

        def process(*args, **kwargs):
            subcon.context['_standby_console_busy'] = True
            raise TimeoutError('timeout')

        with patch('unicon.plugins.iosxe.stack.connection_provider.Dialog') as dialog:
            dialog.return_value.process.side_effect = process
            provider._attach_standby_console(subcon)

        self.assertEqual(dialog.return_value.process.call_count, 1)
        self.assertFalse(getattr(subcon, '_standby_console_attached', False))


class TestFindStandbyConsole(unittest.TestCase):
    """A console attach is only needed when *no* console is on the standby."""

    def _provider(self, outputs):
        con = MagicMock()
        con._subconnections = {
            alias: make_subcon(out, alias) for alias, out in outputs.items()
        }
        provider = make_provider(con)
        provider._release_stale_console_attach = MagicMock()
        return provider

    def test_all_consoles_active_returns_none(self):
        provider = self._provider({'peer_1': SHOW_SWITCH_ACTIVE,
                                   'peer_2': SHOW_SWITCH_ACTIVE,
                                   'peer_3': SHOW_SWITCH_ACTIVE})
        self.assertIsNone(provider._find_standby_console())

    def test_returns_alias_of_standby_console(self):
        provider = self._provider({'peer_1': SHOW_SWITCH_ACTIVE,
                                   'peer_2': SHOW_SWITCH_STANDBY,
                                   'peer_3': SHOW_SWITCH_ACTIVE})
        self.assertEqual(provider._find_standby_console(), 'peer_2')

    def test_finds_standby_that_is_not_the_designated_handle(self):
        """The designation is positional, so the standby can be any console."""
        provider = self._provider({'peer_1': SHOW_SWITCH_ACTIVE,
                                   'peer_2': SHOW_SWITCH_ACTIVE,
                                   'peer_3': SHOW_SWITCH_STANDBY})
        self.assertEqual(provider._find_standby_console(), 'peer_3')

    def test_unreadable_console_does_not_claim_standby(self):
        provider = self._provider({'peer_1': 'show switch\nSwitch#',
                                   'peer_2': 'show switch\nSwitch#'})
        self.assertIsNone(provider._find_standby_console())

    def test_stale_attach_is_cleared_before_probing(self):
        """Otherwise a leftover '-stby#' is mistaken for a real standby."""
        provider = self._provider({'peer_1': SHOW_SWITCH_ACTIVE,
                                   'peer_2': SHOW_SWITCH_ACTIVE})
        provider._find_standby_console()
        self.assertEqual(provider._release_stale_console_attach.call_count, 2)


class TestInitStandby(unittest.TestCase):

    def _connection(self, attach_enabled=True):
        con = MagicMock()
        con.settings.STACK_STANDBY_CONSOLE_ATTACH = attach_enabled
        con.standby.alias = 'peer_2'
        return con

    def test_attaches_when_no_console_reaches_standby(self):
        con = self._connection()
        provider = make_provider(con)
        provider._find_standby_console = MagicMock(return_value=None)
        provider._attach_standby_console = MagicMock()
        provider._get_local_switch = MagicMock(return_value=('3', 'Standby'))

        with patch('unicon.bases.routers.connection_provider.'
                   'BaseStackRpConnectionProvider.init_standby'):
            provider.init_standby()

        provider._attach_standby_console.assert_called_once_with(con.standby)

    def test_does_not_attach_when_a_console_is_on_standby(self):
        con = self._connection()
        provider = make_provider(con)
        provider._find_standby_console = MagicMock(return_value='peer_2')
        provider._attach_standby_console = MagicMock()

        with patch('unicon.bases.routers.connection_provider.'
                   'BaseStackRpConnectionProvider.init_standby'):
            provider.init_standby()

        provider._attach_standby_console.assert_not_called()

    def test_warns_when_standby_console_is_not_the_standby_handle(self):
        con = self._connection()
        provider = make_provider(con)
        provider._find_standby_console = MagicMock(return_value='peer_3')
        provider._attach_standby_console = MagicMock()

        with patch('unicon.bases.routers.connection_provider.'
                   'BaseStackRpConnectionProvider.init_standby'):
            provider.init_standby()

        provider._attach_standby_console.assert_not_called()
        self.assertTrue(con.log.warning.called)

    def test_disabled_setting_is_a_no_op(self):
        """Must not change behaviour on platforms with a real standby console."""
        con = self._connection(attach_enabled=False)
        provider = make_provider(con)
        provider._find_standby_console = MagicMock()
        provider._attach_standby_console = MagicMock()

        with patch('unicon.bases.routers.connection_provider.'
                   'BaseStackRpConnectionProvider.init_standby'):
            provider.init_standby()

        provider._find_standby_console.assert_not_called()
        provider._attach_standby_console.assert_not_called()


class TestSkipHeavyInitCommands(unittest.TestCase):
    """'show version' stalls on the rate-limited standby RP console."""

    def _provider(self, attached):
        con = MagicMock()
        con.settings.STACK_STANDBY_CONSOLE_SKIP_INIT_COMMANDS = ['show version']
        con.standby._standby_console_attached = attached
        provider = make_provider(con)
        return provider

    def _run(self, provider):
        base = ('unicon.bases.routers.connection_provider.'
                'BaseStackRpConnectionProvider.set_init_commands')

        def fake(self_):
            self_.init_exec_commands = ['term length 0', 'term width 0',
                                        'show version']

        with patch(base, new=fake):
            provider.set_init_commands()
        return provider.init_exec_commands

    def test_show_version_dropped_when_console_attached(self):
        provider = self._provider(attached=True)
        self.assertEqual(self._run(provider),
                         ['term length 0', 'term width 0'])

    def test_full_command_set_kept_when_not_attached(self):
        provider = self._provider(attached=False)
        self.assertEqual(self._run(provider),
                         ['term length 0', 'term width 0', 'show version'])


class TestDetachOnDisconnect(unittest.TestCase):

    def test_detaches_only_attached_subconnections(self):
        attached = MagicMock()
        attached._standby_console_attached = True
        plain = MagicMock()
        plain._standby_console_attached = False

        con = MagicMock()
        con.subconnections = [attached, plain]
        provider = make_provider(con)
        provider._detach_standby_console = MagicMock()

        with patch('unicon.bases.routers.connection_provider.'
                   'BaseStackRpConnectionProvider.disconnect'):
            provider.disconnect()

        provider._detach_standby_console.assert_called_once_with(attached)

    def test_detach_sends_ctrl_c(self):
        """Ctrl-C exits the attached console; Ctrl-D does not."""
        con = MagicMock()
        provider = make_provider(MagicMock())
        with patch('unicon.plugins.iosxe.stack.connection_provider.time.sleep'):
            provider._detach_standby_console(con)
        con.spawn.send.assert_any_call('\x03')
        self.assertFalse(con._standby_console_attached)

    def test_release_stale_attach_survives_errors(self):
        con = MagicMock()
        con.spawn.send.side_effect = Exception('closed')
        provider = make_provider(MagicMock())
        with patch('unicon.plugins.iosxe.stack.connection_provider.time.sleep'):
            provider._release_stale_console_attach(con)
        self.assertFalse(con._standby_console_attached)


if __name__ == '__main__':
    unittest.main()
