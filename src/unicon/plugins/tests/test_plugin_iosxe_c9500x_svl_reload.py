"""
Unittest for IOSXE/c9500x SVLStackReload service implementation.
"""
import unittest

from unittest.mock import MagicMock, patch
from unicon.eal.dialogs import Dialog
from unicon.plugins.iosxe.cat9k.c9500x.stackwise_virtual.service_implementation import SVLStackReload


class TestSVLStackReload(unittest.TestCase):
    """Test SVLStackReload service implementation."""

    def _make_mock_connection(self):
        """Return a MagicMock connection wired for SVLStackReload."""
        con = MagicMock()
        con.hostname = 'Router'
        con.connection_timeout = 60

        settings = MagicMock()
        settings.STACK_RELOAD_TIMEOUT = 900
        settings.STACK_POST_RELOAD_SLEEP = 0
        settings.POST_RELOAD_WAIT = 0
        settings.RELOAD_POSTCHECK_INTERVAL = 30
        settings.ERROR_PATTERN = []
        settings.LOGIN_PROMPT = 'Username:'
        settings.PASSWORD_PROMPT = 'Password:'
        con.settings = settings

        conn_active = MagicMock()
        conn_active.spawn = MagicMock()
        conn_active.sendline = conn_active.spawn.sendline
        conn_active.context = {'hostname': 'Router'}
        conn_active.alias = 'peer_1'
        conn_active.hostname = 'Router'
        conn_active.state_machine = MagicMock()
        conn_active.state_machine.default_dialog = Dialog([])
        conn_active.settings = settings
        con.active = conn_active
        con.subconnections = [conn_active]

        con.connection_provider = MagicMock()
        con.connection_provider.get_connection_dialog = MagicMock(
            return_value=Dialog([]))
        return con

    @patch('unicon.plugins.iosxe.cat9k.c9500x.stackwise_virtual'
           '.service_implementation.utils')
    @patch('unicon.plugins.iosxe.cat9k.c9500x.stackwise_virtual'
           '.service_implementation.sleep')
    @patch('unicon.eal.dialogs.Dialog.process',
           return_value=MagicMock(match_output=''))
    def test_svl_stack_reload_complete_flow(self, mock_process,
                                            mock_sleep, mock_utils):
        """Test complete flow of SVLStackReload service implementation."""
        mock_utils.is_active_standby_ready.return_value = True
        con = self._make_mock_connection()

        svc = SVLStackReload(con, con.active.context)
        svc.prompt_recovery = False

        svc.call_service(reload_command=None)
        con.active.sendline.assert_called_with('redundancy reload shelf')
        self.assertEqual(mock_process.call_count, 2)
        go_to_calls = con.active.state_machine.go_to.call_args_list
        self.assertEqual(go_to_calls[0][0][0], 'any')
        self.assertEqual(go_to_calls[1][0][0], 'enable')
        con.active.state_machine.detect_state.assert_not_called()

        # Standby readiness check with correct interval
        mock_utils.is_active_standby_ready.assert_called_once()

        # post-reload sleep called
        mock_sleep.assert_called()
        con.disconnect.assert_called_once()
        con.connect.assert_called_once()
        con.connection_provider.init_connection.assert_not_called()
        con.log.addHandler.assert_called()
        con.log.removeHandler.assert_called()
        self.assertTrue(svc.result)


if __name__ == "__main__":
    unittest.main()
