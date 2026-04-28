"""
Unittest for IOSXE/ASRK HAReload service implementation.
"""
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch, call

import unicon
from unicon import Connection
from unicon.eal.dialogs import Dialog
from unicon.core.errors import SubCommandFailure
from unicon.plugins.generic.service_implementation import ReloadResult
from unicon.plugins.iosxe.asrk.service_implementation import HAReload
from unicon.plugins.tests.mock.mock_device_iosxe import (
    MockDeviceTcpWrapperIOSXE, MockDeviceIOSXE)


class TestASRKHAReload(unittest.TestCase):
    """Test ASRK HAReload service implementation."""

    def _make_mock_connection(self):
        """Return a MagicMock connection wired for ASRK HAReload."""
        con = MagicMock()
        con.hostname = 'Router'
        con.connection_timeout = 60

        settings = MagicMock()
        settings.ERROR_PATTERN = []
        settings.LOGIN_PROMPT = 'Username:'
        settings.PASSWORD_PROMPT = 'Password:'
        settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT = 50
        settings.RELOAD_POSTCHECK_INTERVAL = 30
        settings.CONFIG_LOCK_RETRIES = 3
        settings.CONFIG_LOCK_RETRY_SLEEP = 1
        con.settings = settings

        # Active subconnection
        conn_active = MagicMock()
        conn_active.spawn = MagicMock()
        conn_active.context = {'hostname': 'Router'}
        conn_active.state_machine = MagicMock()
        conn_active.state_machine.current_state = 'enable'
        conn_active.settings = MagicMock()
        conn_active.settings.HA_INIT_EXEC_COMMANDS = []
        conn_active.settings.HA_INIT_CONFIG_COMMANDS = []
        conn_active.settings.CONFIG_POST_RELOAD_RETRY_DELAY_SEC = 1
        conn_active.settings.CONFIG_POST_RELOAD_MAX_RETRIES = 3
        conn_active.settings.CONFIG_LOCK_RETRIES = 3
        conn_active.settings.CONFIG_LOCK_RETRY_SLEEP = 1
        con.active = conn_active

        # Standby subconnection
        conn_standby = MagicMock()
        conn_standby.spawn = MagicMock()
        conn_standby.context = {'hostname': 'Router'}
        conn_standby.state_machine = MagicMock()
        conn_standby.state_machine.current_state = 'enable'
        conn_standby.settings = settings
        con.standby = conn_standby

        con.subconnections = [conn_active, conn_standby]
        con.connection_provider = MagicMock()
        con.connection_provider.get_connection_dialog.return_value = Dialog([])

        return con

    def _make_service(self, con):
        """Create an HAReload service instance with mocked internals."""
        svc = HAReload(con, con.active.context)
        svc.prompt_recovery = False
        svc.timeout = 60
        svc.dialog = Dialog([])
        svc.log_buffer = StringIO()
        svc.error_pattern = []
        svc.context = {}
        svc.get_sm = MagicMock()
        svc.get_sm.return_value.current_state = 'enable'
        svc.get_service_result = MagicMock()
        return svc

    @patch('unicon.plugins.iosxe.asrk.service_implementation.utils')
    @patch('unicon.plugins.iosxe.asrk.service_implementation.custom_auth_statements',
           return_value=[])
    @patch('unicon.eal.dialogs.Dialog.process',
           return_value=MagicMock(match_output='reload output'))
    def test_reload_complete_flow(self, mock_process, mock_auth, mock_utils):
        """Test complete HA reload flow succeeds."""
        mock_utils.is_active_standby_ready.return_value = True
        con = self._make_mock_connection()
        svc = self._make_service(con)

        svc.call_service(reload_command='reload')

        # Reload command sent on active spawn
        con.active.spawn.sendline.assert_any_call('reload')

        # ThreadPoolExecutor should have called dialog.process twice
        # (once for active, once for standby)
        self.assertEqual(mock_process.call_count, 2)

        # Active RP brought to 'any' state during parallel processing
        active_go_to_calls = con.active.state_machine.go_to.call_args_list
        active_states = [c[0][0] for c in active_go_to_calls]
        self.assertIn('any', active_states)

        # disconnect + connect called to re-establish connections
        con.disconnect.assert_called_once()
        con.connect.assert_called_once()

        # is_active_standby_ready called
        mock_utils.is_active_standby_ready.assert_called_once()

        self.assertTrue(svc.result)

    @patch('unicon.plugins.iosxe.asrk.service_implementation.utils')
    @patch('unicon.plugins.iosxe.asrk.service_implementation.custom_auth_statements',
           return_value=[])
    @patch('unicon.eal.dialogs.Dialog.process',
           return_value=MagicMock(match_output='reload output'))
    def test_reload_with_return_output(self, mock_process, mock_auth,
                                       mock_utils):
        """Test reload returns ReloadResult when return_output=True."""
        mock_utils.is_active_standby_ready.return_value = True
        con = self._make_mock_connection()
        svc = self._make_service(con)

        svc.call_service(reload_command='reload', return_output=True)

        self.assertIsInstance(svc.result, ReloadResult)

    @patch('unicon.plugins.iosxe.asrk.service_implementation.utils')
    @patch('unicon.plugins.iosxe.asrk.service_implementation.custom_auth_statements',
           return_value=[])
    @patch('unicon.eal.dialogs.Dialog.process',
           return_value=MagicMock(match_output='reload output'))
    def test_reload_standby_not_ready(self, mock_process, mock_auth,
                                      mock_utils):
        """Test reload completes even when standby does not reach STANDBY HOT."""
        mock_utils.is_active_standby_ready.return_value = False
        con = self._make_mock_connection()
        svc = self._make_service(con)

        svc.call_service(reload_command='reload')

        # Should still succeed; standby not ready is a warning, not failure
        self.assertTrue(svc.result)
        mock_utils.is_active_standby_ready.assert_called_once()

    @patch('unicon.plugins.iosxe.asrk.service_implementation.utils')
    @patch('unicon.plugins.iosxe.asrk.service_implementation.custom_auth_statements',
           return_value=[])
    @patch('unicon.eal.dialogs.Dialog.process')
    def test_reload_active_exception_raises(self, mock_process, mock_auth,
                                            mock_utils):
        """Test that exception in active RP processing is raised."""
        mock_process.side_effect = Exception('Active RP dialog failed')
        con = self._make_mock_connection()
        svc = self._make_service(con)

        with self.assertRaises(SubCommandFailure) as ctx:
            svc.call_service(reload_command='reload')

        self.assertIn('Reload failed', str(ctx.exception))

    @patch('unicon.plugins.iosxe.asrk.service_implementation.utils')
    @patch('unicon.plugins.iosxe.asrk.service_implementation.custom_auth_statements',
           return_value=[])
    @patch('unicon.eal.dialogs.Dialog.process',
           return_value=MagicMock(match_output='reload output'))
    def test_reload_uses_command_parameter(self, mock_process, mock_auth,
                                           mock_utils):
        """Test that 'command' parameter is used as reload command."""
        mock_utils.is_active_standby_ready.return_value = True
        con = self._make_mock_connection()
        svc = self._make_service(con)

        svc.call_service(command='reload force')

        con.active.spawn.sendline.assert_any_call('reload force')

    @patch('unicon.plugins.iosxe.asrk.service_implementation.utils')
    @patch('unicon.plugins.iosxe.asrk.service_implementation.custom_auth_statements',
           return_value=[])
    @patch('unicon.eal.dialogs.Dialog.process',
           return_value=MagicMock(match_output='reload output'))
    def test_reload_with_reload_creds(self, mock_process, mock_auth,
                                      mock_utils):
        """Test reload with custom reload credentials."""
        mock_utils.is_active_standby_ready.return_value = True
        con = self._make_mock_connection()
        svc = self._make_service(con)

        svc.call_service(reload_command='reload',
                         reload_creds=['admin', 'password'])

        # Verify call succeeds with reload_creds
        self.assertTrue(svc.result)

    @patch('unicon.plugins.iosxe.asrk.service_implementation.utils')
    @patch('unicon.plugins.iosxe.asrk.service_implementation.custom_auth_statements',
           return_value=[])
    @patch('unicon.eal.dialogs.Dialog.process',
           return_value=MagicMock(match_output='reload output'))
    def test_reload_error_pattern_validation(self, mock_process, mock_auth,
                                             mock_utils):
        """Test that error_pattern must be a list."""
        mock_utils.is_active_standby_ready.return_value = True
        con = self._make_mock_connection()
        svc = self._make_service(con)

        with self.assertRaises(ValueError):
            svc.call_service(reload_command='reload',
                             error_pattern='not a list')

    @patch('unicon.plugins.iosxe.asrk.service_implementation.utils')
    @patch('unicon.plugins.iosxe.asrk.service_implementation.custom_auth_statements',
           return_value=[])
    @patch('unicon.eal.dialogs.Dialog.process',
           return_value=MagicMock(match_output='reload output'))
    def test_reload_append_error_pattern(self, mock_process, mock_auth,
                                         mock_utils):
        """Test that append_error_pattern extends error patterns."""
        mock_utils.is_active_standby_ready.return_value = True
        con = self._make_mock_connection()
        svc = self._make_service(con)

        svc.call_service(reload_command='reload',
                         append_error_pattern=['extra_error'])

        self.assertIn('extra_error', svc.error_pattern)

    @patch('unicon.plugins.iosxe.asrk.service_implementation.utils')
    @patch('unicon.plugins.iosxe.asrk.service_implementation.custom_auth_statements',
           return_value=[])
    @patch('unicon.eal.dialogs.Dialog.process',
           return_value=MagicMock(match_output='reload output'))
    def test_reload_standby_rommon_transition(self, mock_process, mock_auth,
                                              mock_utils):
        """Test standby in rommon is transitioned to disable state."""
        mock_utils.is_active_standby_ready.return_value = True
        con = self._make_mock_connection()
        con.standby.state_machine.current_state = 'rommon'
        svc = self._make_service(con)

        svc.call_service(reload_command='reload')

        # Standby should have go_to('disable') called for rommon recovery
        standby_go_to_calls = con.standby.state_machine.go_to.call_args_list
        standby_states = [c[0][0] for c in standby_go_to_calls]
        self.assertIn('disable', standby_states)

    @patch('unicon.plugins.iosxe.asrk.service_implementation.utils')
    @patch('unicon.plugins.iosxe.asrk.service_implementation.custom_auth_statements',
           return_value=[])
    @patch('unicon.eal.dialogs.Dialog.process',
           return_value=MagicMock(match_output='reload output'))
    def test_reload_config_lock_settings_restored(self, mock_process,
                                                   mock_auth, mock_utils):
        """Test CONFIG_LOCK settings are restored after configure."""
        mock_utils.is_active_standby_ready.return_value = True
        con = self._make_mock_connection()
        svc = self._make_service(con)

        original_retries = con.settings.CONFIG_LOCK_RETRIES
        original_sleep = con.settings.CONFIG_LOCK_RETRY_SLEEP

        svc.call_service(reload_command='reload')

        self.assertEqual(con.settings.CONFIG_LOCK_RETRIES, original_retries)
        self.assertEqual(con.settings.CONFIG_LOCK_RETRY_SLEEP, original_sleep)

    @patch('unicon.plugins.iosxe.asrk.service_implementation.utils')
    @patch('unicon.plugins.iosxe.asrk.service_implementation.custom_auth_statements',
           return_value=[])
    @patch('unicon.eal.dialogs.Dialog.process',
           return_value=MagicMock(match_output='reload output'))
    def test_reload_golden_image_recovery(self, mock_process, mock_auth,
                                          mock_utils):
        """Test golden image recovery on reload failure."""
        # Make standby go_to('any') fail to trigger exception path
        con = self._make_mock_connection()
        con.standby.state_machine.go_to.side_effect = Exception('standby failed')
        con.settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT = 0

        # Set up golden image recovery
        con.device = MagicMock()
        con.device.clean.device_recovery = {
            'golden_image': 'bootflash:/golden.bin'
        }

        svc = self._make_service(con)

        with self.assertRaises(SubCommandFailure):
            svc.call_service(reload_command='reload')

        con.device.api.device_recovery_boot.assert_called_once_with(
            golden_image='bootflash:/golden.bin')

    @patch('unicon.plugins.iosxe.asrk.service_implementation.utils')
    @patch('unicon.plugins.iosxe.asrk.service_implementation.custom_auth_statements',
           return_value=[])
    @patch('unicon.eal.dialogs.Dialog.process',
           return_value=MagicMock(match_output='reload output'))
    def test_reload_log_handlers_cleaned_up(self, mock_process, mock_auth,
                                            mock_utils):
        """Test log handlers are added then removed."""
        mock_utils.is_active_standby_ready.return_value = True
        con = self._make_mock_connection()
        svc = self._make_service(con)

        svc.call_service(reload_command='reload')

        # Log handlers should be added and removed
        con.log.addHandler.assert_called()
        con.log.removeHandler.assert_called()
        for subcon in con.subconnections:
            subcon.log.addHandler.assert_called()
            subcon.log.removeHandler.assert_called()

    @patch('unicon.plugins.iosxe.asrk.service_implementation.utils')
    @patch('unicon.plugins.iosxe.asrk.service_implementation.custom_auth_statements',
           return_value=[])
    @patch('unicon.eal.dialogs.Dialog.process',
           return_value=MagicMock(match_output='reload output'))
    def test_reload_from_rommon_sets_boot_cmd(self, mock_process, mock_auth,
                                              mock_utils):
        """Test that boot_cmd is set when in rommon state."""
        mock_utils.is_active_standby_ready.return_value = True
        con = self._make_mock_connection()
        svc = self._make_service(con)
        svc.get_sm.return_value.current_state = 'rommon'

        svc.call_service(reload_command='boot bootflash:/image.bin')

        self.assertEqual(con.active.context['boot_cmd'],
                         'boot bootflash:/image.bin')


class TestGenericUtilsIsActiveStandbyReady(unittest.TestCase):
    """Test GenericUtils.is_active_standby_ready method."""

    def setUp(self):
        from unicon.plugins.generic.utils import GenericUtils
        self.utils = GenericUtils()

    def _make_mock_connection(self):
        con = MagicMock()
        con.log = MagicMock()
        return con

    @patch('unicon.plugins.generic.utils.time')
    def test_returns_true_when_both_ready(self, mock_time):
        """Test returns True when active=ACTIVE and standby=STANDBY HOT."""
        mock_time.time.side_effect = [0, 1]  # start, first check
        con = self._make_mock_connection()
        con.execute.return_value = """
Redundancy Mode (Operational) = sso

Current Processor Information :
-------------------------------
Active Location = slot 6
Current Software state = ACTIVE
Uptime in current state = 3 days, 4 hours

Peer Processor Information :
----------------------------
Standby Location = slot 7
Current Software state = STANDBY HOT
Uptime in current state = 3 days, 4 hours
"""
        result = self.utils.is_active_standby_ready(
            con, timeout=120, interval=30)
        self.assertTrue(result)

    @patch('unicon.plugins.generic.utils.time')
    def test_returns_false_on_timeout(self, mock_time):
        """Test returns False when standby never reaches STANDBY HOT."""
        # Simulate time passing beyond timeout
        mock_time.time.side_effect = [0, 10, 50, 130]
        mock_time.sleep = MagicMock()
        con = self._make_mock_connection()
        con.execute.return_value = """
Current Processor Information :
-------------------------------
Current Software state = ACTIVE

Peer Processor Information :
----------------------------
Current Software state = DISABLED
"""
        result = self.utils.is_active_standby_ready(
            con, timeout=120, interval=30)
        self.assertFalse(result)

    @patch('unicon.plugins.generic.utils.time')
    def test_retries_on_execute_exception(self, mock_time):
        """Test retries when show redundancy fails."""
        mock_time.time.side_effect = [0, 10, 50, 130]
        mock_time.sleep = MagicMock()
        con = self._make_mock_connection()
        con.execute.side_effect = Exception('Connection error')

        result = self.utils.is_active_standby_ready(
            con, timeout=120, interval=30)
        self.assertFalse(result)
        con.log.error.assert_called()

    @patch('unicon.plugins.generic.utils.time')
    def test_handles_missing_peer_section(self, mock_time):
        """Test handles output with no Peer Processor section."""
        mock_time.time.side_effect = [0, 10, 130]
        mock_time.sleep = MagicMock()
        con = self._make_mock_connection()
        con.execute.return_value = """
Current Processor Information :
-------------------------------
Current Software state = ACTIVE
"""
        result = self.utils.is_active_standby_ready(
            con, timeout=120, interval=30)
        self.assertFalse(result)


class NoInterChangeConsoleMockDeviceIOSXEASRK(MockDeviceIOSXE):
    """Mock device that handles ASRK HA reload with dual-RP switchover."""

    def ha_asrk_active_reload_proceed(self, transport, cmd):
        if 'prompt' in self.transport_ports[self.transport_handles[transport]]:
            prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
            if cmd == "" and prompt == 'Proceed with reload? [confirm]':
                if len(self.transport_ports) > 1:
                    self.state_change_switchover(
                        transport, 'ha_asrk_active_reload_boot',
                        'ha_asrk_standby_boot')
                return True


class TestASRKHAReloadMockDevice(unittest.TestCase):
    """Test ASRK HAReload using mock device with TCP wrapper."""

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperIOSXE(
            hostname='Router',
            port=0,
            state='ha_asrk_active_disable,ha_asrk_standby_disable')
        cls.md.mockdevice = NoInterChangeConsoleMockDeviceIOSXEASRK(
            state='ha_asrk_active_disable,ha_asrk_standby_disable',
            hostname='Router')
        cls.md.start()

        cls.con = Connection(
            hostname='Router',
            start=[
                'telnet 127.0.0.1 {}'.format(cls.md.ports[0]),
                'telnet 127.0.0.1 {}'.format(cls.md.ports[1]),
            ],
            os='iosxe',
            platform='asrk',
            credentials=dict(
                default=dict(username='admin', password='lab'),
            ),
            settings=dict(
                POST_DISCONNECT_WAIT_SEC=0,
                GRACEFUL_DISCONNECT_WAIT_SEC=0.2,
            ),
            log_buffer=True,
        )
        cls.con.connect()

    @classmethod
    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def tearDownClass(cls):
        cls.con.disconnect()
        cls.md.stop()

    def test_asrk_ha_reload(self):
        """Test ASRK HA reload with mock device completes successfully."""
        self.con.settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT = 0
        self.con.settings.POST_RELOAD_WAIT = 1
        result = self.con.reload(reload_command='reload')
        self.assertTrue(result)
        self.assertEqual(self.con.active.state_machine.current_state, 'enable')


if __name__ == '__main__':
    unittest.main()
