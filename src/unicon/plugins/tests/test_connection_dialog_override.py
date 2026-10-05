"""Tests for provider-specific replacement connection dialogs."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from unicon.bases.routers.connection_provider import (
    BaseSingleRpConnectionProvider,
)
from unicon import Connection
from unicon.eal.dialogs import Dialog, Statement
from unicon.plugins.generic.connection_provider import (
    GenericDualRpConnectionProvider,
    GenericSingleRpConnectionProvider,
)
from unicon.plugins.generic.statements import connection_statement_list
from unicon.plugins.aireos.connection_provider import (
    AireosDualRpConnectionProvider,
)
from unicon.plugins.iosxe.cat4k.connection_provider import (
    Cat4kDualRpConnectionProvider,
)
from unicon.plugins.iosxe.connection_provider import (
    IosxeSingleRpConnectionProvider,
)
from unicon.plugins.iosxe.cat9k.stackwise_virtual.connection_provider import (
    StackwiseVirtualConnectionProvider,
)
from unicon.plugins.iosxr.connection_provider import (
    IOSXRDualRpConnectionProvider,
    IOSXRSingleRpConnectionProvider,
)
from unicon.plugins.iosxr.iosxrv.connection_provider import (
    IOSXRVDualRpConnectionProvider,
    IOSXRVSingleRpConnectionProvider,
)
from unicon.plugins.iosxr.iosxrv9k.connection_provider import (
    IOSXRV9KSingleRpConnectionProvider,
)
from unicon.plugins.nxos import NxosSingleRpConnectionProvider
from unicon.plugins.nxos.n7k.connection_provider import (
    Nxos7kSingleRpConnectionProvider,
)


def replacement_dialog():
    return Dialog([Statement(pattern='break boot activity')])


def single_rp_connection():
    state_machine = Mock()
    state_machine.current_state = 'rommon'
    connection = SimpleNamespace(
        prompt_recovery=False,
        state_machine=state_machine,
        settings=SimpleNamespace(DEFAULT_LEARNED_HOSTNAME='uut'),
        context={},
        spawn=Mock(),
        connection_timeout=10,
        device=None,
    )
    return connection, state_machine


def subconnection(alias='peer_1'):
    state_machine = Mock()
    state_machine.current_state = 'rommon'
    state_machine.get_state.return_value.pattern = r'^.*>$'
    spawn = Mock()
    spawn.match.match_output = 'switch:'
    return SimpleNamespace(
        alias=alias,
        context={},
        connection_timeout=10,
        learn_hostname=False,
        learned_hostname=False,
        prompt_recovery=False,
        state_machine=state_machine,
        spawn=spawn,
        sendline=Mock(),
        log=Mock(),
    )


def multi_rp_connection(subconnections):
    connection = SimpleNamespace(
        prompt_recovery=False,
        subconnections=subconnections,
        _subconnections={sub.alias: sub for sub in subconnections},
        settings=SimpleNamespace(
            DEFAULT_LEARNED_HOSTNAME='uut',
            STACK_BOOT_TIMEOUT=10,
        ),
        context={},
        connection_timeout=10,
        device=None,
        log=Mock(),
    )

    def _find_connection_refused_error(error):
        seen = set()
        while error is not None and id(error) not in seen:
            seen.add(id(error))
            if isinstance(error, ConnectionRefusedError):
                return error
            error = error.__cause__ or error.__context__
        return None

    connection._find_connection_refused_error = \
        _find_connection_refused_error
    return connection


class TestConnectionDialogOverride(unittest.TestCase):

    def test_state_detection_only_learns_enable_over_stale_rommon(self):
        """Actual state detection stops before IOS XE token discovery."""
        connection = Connection(
            hostname='Router',
            start=[
                'mock_device_cli --os iosxe '
                '--state general_enable_no_operating_mode '
                '--hostname Router'
            ],
            os='iosxe',
            mit=True,
            connection_timeout=5,
            init_exec_commands=[],
            init_config_commands=[],
        )
        connection.state_machine.update_cur_state('rommon')

        try:
            with patch.object(
                    GenericSingleRpConnectionProvider,
                    'get_connection_dialog',
                    side_effect=AssertionError(
                        'standard connection dialog must not be used')), \
                    patch.object(
                        IosxeSingleRpConnectionProvider,
                        'learn_tokens',
                        side_effect=AssertionError(
                            'token discovery must not run')):
                connection.connect(
                    connection_dialog=Dialog([]),
                    skip_initialization=True)

            self.assertEqual(
                connection.state_machine.current_state, 'enable')
        finally:
            connection.disconnect()

    @patch(
        'unicon.plugins.iosxe.connection_provider.get_device_mode',
        return_value='Autonomous',
    )
    def test_iosxe_learn_tokens_preserves_default_probe(self, _get_mode):
        connection = Mock()
        connection.learn_tokens = False
        connection.settings.LEARN_DEVICE_TOKENS = False
        connection.operating_mode = False
        connection.prompt_recovery = False
        provider = IosxeSingleRpConnectionProvider(connection)
        provider.get_connection_dialog = Mock(
            side_effect=AssertionError('default dialog must not be added'))

        with patch.object(
                BaseSingleRpConnectionProvider, 'learn_tokens') as parent:
            provider.learn_tokens()

        provider.get_connection_dialog.assert_not_called()
        go_to_kwargs = connection.state_machine.go_to.call_args.kwargs
        self.assertNotIn('dialog', go_to_kwargs)
        self.assertNotIn('dialog_replacement', go_to_kwargs)
        parent.assert_called_once_with()

    @patch(
        'unicon.plugins.iosxe.connection_provider.get_device_mode',
        return_value='Autonomous',
    )
    def test_iosxe_learn_tokens_replaces_probe_dialog(self, _get_mode):
        connection = Mock()
        connection.learn_tokens = False
        connection.settings.LEARN_DEVICE_TOKENS = False
        connection.operating_mode = False
        connection.prompt_recovery = False
        provider = IosxeSingleRpConnectionProvider(connection)
        provider.get_connection_dialog = Mock(
            side_effect=AssertionError('default dialog must not be used'))
        dialog = Dialog([])

        with patch.object(BaseSingleRpConnectionProvider, 'learn_tokens'):
            provider.learn_tokens(connection_dialog=dialog)

        provider.get_connection_dialog.assert_not_called()
        go_to_kwargs = connection.state_machine.go_to.call_args.kwargs
        self.assertIs(go_to_kwargs['dialog'], dialog)
        self.assertTrue(go_to_kwargs['dialog_replacement'])

    def test_iosxe_learn_tokens_preserves_replacement_on_redirect(self):
        connection = Mock()
        connection.operating_mode = True
        provider = IosxeSingleRpConnectionProvider(connection)
        dialog = Dialog([])

        with patch.object(
                BaseSingleRpConnectionProvider, 'learn_tokens') as parent:
            provider.learn_tokens(connection_dialog=dialog)

        parent.assert_called_once_with(connection_dialog=dialog)

    @patch(
        'unicon.plugins.iosxe.connection_provider.get_device_mode',
        side_effect=AssertionError('controller detection must not run'),
    )
    def test_iosxe_skip_initialization_stops_after_enable_detection(
            self, get_device_mode):
        connection, state_machine = single_rp_connection()
        state_machine.current_state = 'enable'
        connection.enable = Mock()
        provider = IosxeSingleRpConnectionProvider(connection)
        provider.learn_hostname = Mock()
        provider.learn_tokens = Mock()

        provider.establish_connection(
            connection_dialog=Dialog([]), skip_initialization=True)

        state_machine.go_to.assert_called_once()
        connection.enable.assert_not_called()
        provider.learn_hostname.assert_not_called()
        provider.learn_tokens.assert_not_called()
        get_device_mode.assert_not_called()

    def test_generic_single_uses_only_replacement_dialog(self):
        connection, state_machine = single_rp_connection()
        provider = GenericSingleRpConnectionProvider(connection)
        provider.get_connection_dialog = Mock(
            side_effect=AssertionError('standard dialog must not be used'))
        dialog = replacement_dialog()

        provider.establish_connection(connection_dialog=dialog)

        provider.get_connection_dialog.assert_not_called()
        self.assertIs(state_machine.go_to.call_args.kwargs['dialog'], dialog)
        self.assertTrue(
            state_machine.go_to.call_args.kwargs['dialog_replacement'])

    def test_generic_dual_uses_only_replacement_dialog(self):
        subcon = subconnection()
        provider = GenericDualRpConnectionProvider(
            multi_rp_connection([subcon]))
        provider.get_connection_dialog = Mock(
            side_effect=AssertionError('standard dialog must not be used'))
        dialog = replacement_dialog()

        provider.establish_connection(connection_dialog=dialog)

        provider.get_connection_dialog.assert_not_called()
        for go_to_call in subcon.state_machine.go_to.call_args_list:
            self.assertIs(go_to_call.kwargs['dialog'], dialog)
            self.assertTrue(go_to_call.kwargs['dialog_replacement'])

    def test_stackwise_virtual_uses_only_replacement_dialog(self):
        subcon = subconnection()
        provider = StackwiseVirtualConnectionProvider(
            multi_rp_connection([subcon]))
        provider.get_connection_dialog = Mock(
            side_effect=AssertionError('standard dialog must not be used'))
        dialog = replacement_dialog()

        provider.establish_connection(connection_dialog=dialog)

        provider.get_connection_dialog.assert_not_called()
        self.assertIs(
            subcon.state_machine.go_to.call_args.kwargs['dialog'], dialog)
        self.assertTrue(
            subcon.state_machine.go_to.call_args.kwargs['dialog_replacement'])
        subcon.sendline.assert_not_called()

    def test_aireos_dual_forwards_replacement_dialog(self):
        connection = Mock()
        connection.prompt_recovery = False
        connection.a.spawn = Mock()
        connection.b.spawn = Mock()
        connection.mit = True
        provider = AireosDualRpConnectionProvider(connection)
        provider.establish_connection = Mock()
        dialog = Dialog([])

        provider.connect(connection_dialog=dialog)

        provider.establish_connection.assert_called_once_with(
            connection_dialog=dialog)
        provider.establish_connection.reset_mock()

        provider.connect(
            connection_dialog=dialog, skip_initialization=True)

        provider.establish_connection.assert_called_once_with(
            connection_dialog=dialog, skip_initialization=True)

    def test_iosxr_single_forwards_replacement_dialog(self):
        connection = Mock()
        connection.prompt_recovery = False
        connection.context = {}
        connection.state_machine.current_state = 'rommon'
        provider = IOSXRSingleRpConnectionProvider(connection)
        dialog = Dialog([])

        with patch.object(
                BaseSingleRpConnectionProvider,
                'establish_connection',
                return_value='connected') as parent:
            output = provider.establish_connection(
                connection_dialog=dialog)

            self.assertEqual(output, 'connected')
            parent.assert_called_once_with(connection_dialog=dialog)
            parent.reset_mock()

            output = provider.establish_connection(
                connection_dialog=dialog, skip_initialization=True)

        self.assertEqual(output, 'connected')
        parent.assert_called_once_with(
            connection_dialog=dialog, skip_initialization=True)

    def test_iosxr_dual_forwards_replacement_dialog(self):
        connection = Mock()
        connection.prompt_recovery = False
        connection.subconnections = []
        connection.learn_tokens = False
        connection.settings.LEARN_DEVICE_TOKENS = False
        connection.mit = True
        provider = IOSXRDualRpConnectionProvider(connection)
        provider.establish_connection = Mock()
        dialog = Dialog([])

        provider.connect(connection_dialog=dialog)

        provider.establish_connection.assert_called_once_with(
            connection_dialog=dialog)
        provider.establish_connection.reset_mock()

        provider.connect(
            connection_dialog=dialog, skip_initialization=True)

        provider.establish_connection.assert_called_once_with(
            connection_dialog=dialog, skip_initialization=True)

    def _iosxr_virtual_connection(self):
        settings = SimpleNamespace(
            SLEEP_PRE_LAUNCH=0,
            INITIAL_LAUNCH_DISCOVERY_WAIT_SEC=1,
            INITIAL_LAUNCH_WAIT_SEC=1,
            POST_PROMPT_WAIT_SEC=1,
        )
        return SimpleNamespace(
            prompt_recovery=False,
            settings=settings,
            learn_hostname=False,
            log=Mock(),
            hostname='uut',
        )

    @patch('unicon.plugins.iosxr.iosxrv.connection_provider.time.sleep')
    def test_iosxrv_single_replacement_skips_launch_dialog(
            self, mock_sleep):
        connection = self._iosxr_virtual_connection()
        provider = IOSXRVSingleRpConnectionProvider(connection)
        provider.wait_for_launch_complete = Mock()
        dialog = Dialog([])

        with patch.object(
                IOSXRSingleRpConnectionProvider,
                'establish_connection') as parent:
            provider.establish_connection(connection_dialog=dialog)

            parent.assert_called_once_with(connection_dialog=dialog)
            parent.reset_mock()

            provider.establish_connection(
                connection_dialog=dialog, skip_initialization=True)

        mock_sleep.assert_not_called()
        provider.wait_for_launch_complete.assert_not_called()
        parent.assert_called_once_with(
            connection_dialog=dialog, skip_initialization=True)

    @patch('unicon.plugins.iosxr.iosxrv.connection_provider.time.sleep')
    def test_iosxrv_single_default_keeps_launch_dialog(self, mock_sleep):
        connection = self._iosxr_virtual_connection()
        provider = IOSXRVSingleRpConnectionProvider(connection)
        provider.wait_for_launch_complete = Mock()

        with patch.object(
                IOSXRSingleRpConnectionProvider,
                'establish_connection') as parent:
            provider.establish_connection()

        mock_sleep.assert_called_once_with(0)
        provider.wait_for_launch_complete.assert_called_once()
        parent.assert_called_once_with()

    def test_iosxrv_dual_replacement_skips_launch_dialog(self):
        connection = self._iosxr_virtual_connection()
        connection.a = Mock()
        connection.b = Mock()
        provider = IOSXRVDualRpConnectionProvider(connection)
        provider.wait_for_launch_complete = Mock()
        dialog = Dialog([])

        with patch.object(
                IOSXRDualRpConnectionProvider,
                'establish_connection') as parent:
            provider.establish_connection(connection_dialog=dialog)

            parent.assert_called_once_with(connection_dialog=dialog)
            parent.reset_mock()

            provider.establish_connection(
                connection_dialog=dialog, skip_initialization=True)

        provider.wait_for_launch_complete.assert_not_called()
        parent.assert_called_once_with(
            connection_dialog=dialog, skip_initialization=True)

    def test_iosxrv9k_replacement_skips_launch_dialog(self):
        connection = self._iosxr_virtual_connection()
        provider = IOSXRV9KSingleRpConnectionProvider(connection)
        provider.wait_for_launch_complete = Mock()
        dialog = Dialog([])

        with patch.object(
                IOSXRSingleRpConnectionProvider,
                'establish_connection') as parent:
            provider.establish_connection(connection_dialog=dialog)

            parent.assert_called_once_with(connection_dialog=dialog)
            parent.reset_mock()

            provider.establish_connection(
                connection_dialog=dialog, skip_initialization=True)

        provider.wait_for_launch_complete.assert_not_called()
        parent.assert_called_once_with(
            connection_dialog=dialog, skip_initialization=True)

    def test_n7k_forwards_replacement_dialog(self):
        connection = Mock()
        connection.prompt_recovery = False
        connection.spawn.match.last_match.groupdict.return_value = {}
        provider = Nxos7kSingleRpConnectionProvider(connection)
        dialog = Dialog([])

        with patch.object(
                NxosSingleRpConnectionProvider,
                'establish_connection') as parent:
            provider.establish_connection(connection_dialog=dialog)

            parent.assert_called_once_with(connection_dialog=dialog)
            parent.reset_mock()

            provider.establish_connection(
                connection_dialog=dialog, skip_initialization=True)

        parent.assert_called_once_with(
            connection_dialog=dialog, skip_initialization=True)

    def test_cat4k_uses_only_replacement_dialog(self):
        subcon = subconnection()
        provider = Cat4kDualRpConnectionProvider(
            multi_rp_connection([subcon]))
        dialog = replacement_dialog()

        provider.establish_connection(connection_dialog=dialog)

        self.assertIs(
            subcon.state_machine.go_to.call_args.kwargs['dialog'], dialog)
        self.assertTrue(
            subcon.state_machine.go_to.call_args.kwargs['dialog_replacement'])
        subcon.sendline.assert_not_called()

    def test_cat4k_empty_dialog_is_an_explicit_override(self):
        subcon = subconnection()
        provider = Cat4kDualRpConnectionProvider(
            multi_rp_connection([subcon]))
        dialog = Dialog([])

        provider.establish_connection(connection_dialog=dialog)

        self.assertIs(
            subcon.state_machine.go_to.call_args.kwargs['dialog'], dialog)
        self.assertTrue(
            subcon.state_machine.go_to.call_args.kwargs['dialog_replacement'])
        subcon.sendline.assert_not_called()

    def test_cat4k_skip_initialization_stops_after_state_detection(self):
        subcon = subconnection()
        subcon.state_machine.current_state = 'enable'
        subcon.learn_hostname = True
        provider = Cat4kDualRpConnectionProvider(
            multi_rp_connection([subcon]))
        provider.learn_hostname = Mock()

        provider.establish_connection(
            connection_dialog=Dialog([]), skip_initialization=True)

        subcon.state_machine.go_to.assert_called_once()
        provider.learn_hostname.assert_not_called()
        self.assertFalse(subcon.state_machine.learn_hostname)

    def test_cat4k_replacement_propagates_connection_refused(self):
        subcon = subconnection()
        subcon.context['cred_list'] = ['default']
        subcon.state_machine.go_to.side_effect = ConnectionRefusedError(
            'refused')
        provider = Cat4kDualRpConnectionProvider(
            multi_rp_connection([subcon]))

        with self.assertRaisesRegex(ConnectionRefusedError, 'refused'):
            provider.establish_connection(
                connection_dialog=replacement_dialog())

        self.assertNotIn('cred_list', subcon.context)

    def test_cat4k_refusal_is_not_hidden_by_other_console_error(self):
        first = subconnection('peer_1')
        second = subconnection('peer_2')
        first.state_machine.go_to.side_effect = RuntimeError(
            'state detection failed')
        second.state_machine.go_to.side_effect = ConnectionRefusedError(
            'refused')
        provider = Cat4kDualRpConnectionProvider(
            multi_rp_connection([first, second]))

        with self.assertRaisesRegex(ConnectionRefusedError, 'refused'):
            provider.establish_connection(
                connection_dialog=replacement_dialog())

    def test_cat4k_replacement_preserves_state_detection_error(self):
        subcon = subconnection()
        subcon.state_machine.go_to.side_effect = RuntimeError(
            'state detection failed')
        provider = Cat4kDualRpConnectionProvider(
            multi_rp_connection([subcon]))

        with self.assertRaisesRegex(RuntimeError, 'state detection failed'):
            provider.establish_connection(
                connection_dialog=replacement_dialog())

    def test_cat4k_none_preserves_standard_dialog(self):
        subcon = subconnection()
        provider = Cat4kDualRpConnectionProvider(
            multi_rp_connection([subcon]))

        provider.establish_connection()

        dialog = subcon.state_machine.go_to.call_args.kwargs['dialog']
        self.assertEqual(
            dialog.get_pattern_list(),
            Dialog(connection_statement_list).get_pattern_list())
        self.assertNotIn(
            'dialog_replacement',
            subcon.state_machine.go_to.call_args.kwargs)
        subcon.sendline.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
