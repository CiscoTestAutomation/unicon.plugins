"""
Unittests for IOSXR plugin

Uses the mock_device.py script to test IOSXR plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import os
import re
import threading
import unittest
from textwrap import dedent
from types import SimpleNamespace
from unittest.mock import Mock, patch

import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure
from unicon.plugins.tests.mock.mock_device_iosxr import MockDeviceTcpWrapperIOSXR, MockDeviceIOSXR
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path

from unicon.plugins.iosxr.patterns import IOSXRPatterns
from unicon.plugins.iosxr.statements import (
    recover_config_transaction_lock,
)

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXrPlugin(unittest.TestCase):
    def test_login_connect_ssh(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxr --state connect_ssh'],
                       os='iosxr',
                       credentials=dict(default=dict(username='admin', password='admin')))
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRP/0/RP0/CPU0:Router#')

    def test_login_execution(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxr --state enable'],
                       os='iosxr',
                       credentials=dict(default=dict(username='admin', password='admin')))
        c.connect()
        device_output = c.execute('show version')
        with open(os.path.join(mockdata_path, 'iosxr/show_version.txt'), 'r') as outputfile:
            expected_device_output = outputfile.read().strip()
        device_output = device_output.replace('\r', '').strip()
        self.maxDiff = None
        self.assertEqual(device_output, expected_device_output)

    def test_login_ssh_password(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxr --state ssh_password'],
                       os='iosxr',
                       credentials=dict(default=dict(username='admin', password='admin')))
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRP/0/RP0/CPU0:Router#')

    def test_log_message_before_prompt(self):
        c = Connection(hostname='R1',
                       start=['mock_device_cli --hostname R1 --os iosxr --state enable'],
                       os='iosxr',
                       username='cisco',
                       enable_password='admin',
                       init_config_commands=[],
                       init_exec_commands=[])
        c.connect()

        c.settings.IGNORE_CHATTY_TERM_OUTPUT = False
        c.sendline('process_restart_msg')
        r = c.execute('show telemetry | inc ACTIVE')
        self.assertIn(
            """process_restart_msg
0/RP0/ADMIN0:Jul 7 10:07:42.979 UTC: pm[2890]: %INFRA-Process_Manager-3-PROCESS_RESTART : Process tams (IID: 0) restarted""",
            r.replace('\r', '').replace('\n\n', '\n'))

        c.settings.IGNORE_CHATTY_TERM_OUTPUT = True
        c.sendline('process_restart_msg')
        r = c.execute('show telemetry | inc ACTIVE')
        self.assertEqual(r, 'Sat Jul 7 10:08:02.976 UTC\r\nState: ACTIVE')

    def test_connect_prompts(self):
        for state in [
                'sysadmin_config',
                'sysadmin1',
                'sysadmin2',
                'iosxr_config_ios',
                'xr_vm',
                'xr_vm2'
        ]:
            c = Connection(hostname='Router',
                           start=['mock_device_cli --os iosxr --state %s' % state],
                           os='iosxr',
                           enable_password='cisco',
                           init_exec_commands=[],
                           init_config_commands=[])
            try:
                c.connect()
            finally:
                c.disconnect()

    def test_connect_recovers_configuration_inconsistency(self):
        c = Connection(
            hostname='Router',
            start=[
                'mock_device_cli --os iosxr --state config_inconsistent'
            ],
            os='iosxr',
            init_exec_commands=[],
            init_config_commands=[],
            log_buffer=True,
        )
        try:
            c.connect()
            self.assertEqual(c.state_machine.current_state, 'enable')
            self.assertIn(
                'Configuration inconsistency successfully cleared.',
                c.log_buffer,
            )
        finally:
            c.disconnect()

    def test_connect_does_not_clear_other_pending_changes(self):
        c = Connection(
            hostname='Router',
            start=[
                'mock_device_cli --os iosxr --state config_pending_changes'
            ],
            os='iosxr',
            init_exec_commands=[],
            init_config_commands=[],
            log_buffer=True,
        )
        try:
            c.connect()
            self.assertEqual(c.state_machine.current_state, 'enable')
            self.assertNotIn(
                'clear configuration inconsistency\r',
                c.log_buffer,
            )
            self.assertNotIn('_iosxr_initial_connection', c.context)
            self.assertNotIn('_iosxr_uncommitted_changes', c.context)
        finally:
            c.disconnect()

    def test_connect_does_not_clear_in_essential_ops_mode(self):
        c = Connection(
            hostname='Router',
            start=[
                'mock_device_cli --os iosxr --state config_essential_ops'
            ],
            os='iosxr',
            init_exec_commands=[],
            init_config_commands=[],
            log_buffer=True,
        )
        c.settings.CONFIG_LOCK_RETRY_SLEEP = 0
        try:
            c.connect()
            self.assertEqual(
                c.state_machine.current_state,
                'enable',
            )
            self.assertIn('% Invalid command (essential-ops mode)', c.log_buffer)
            self.assertNotIn(
                'clear configuration inconsistency\r',
                c.log_buffer,
            )
        finally:
            c.disconnect()

    def test_connect_recovery_uses_config_transition_handling(self):
        c = Connection(
            hostname='Router',
            start=[
                'mock_device_cli --os iosxr '
                '--state config_inconsistent_proceed'
            ],
            os='iosxr',
            init_exec_commands=[],
            init_config_commands=[],
            log_buffer=True,
        )
        c.settings.CONFIG_LOCK_RETRY_SLEEP = 0
        try:
            c.connect()
            self.assertEqual(c.state_machine.current_state, 'enable')
            self.assertIn(
                'Would you like to proceed in configuration mode?',
                c.log_buffer,
            )
            self.assertIn(
                'Configuration inconsistency successfully cleared.',
                c.log_buffer,
            )
        finally:
            c.disconnect()

    def test_configure_root_system_username(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxr --state configure_root_system_username'],
                       os='iosxr',
                       username='root',
                       tacacs_password='secretpassword')
        c.connect()

    def test_configure_root_system_username_credential(self):
        c = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxr --state configure_root_system_username'],
            os='iosxr',
            credentials=dict(default=dict(username='root', password='secretpassword')),
        )
        c.connect()

    def test_connect_learn_hostname(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxr --state enable --hostname xrv-ss-test1'],
                       os='iosxr',
                       init_exec_commands=[],
                       init_config_commands=[],
                       learn_hostname=True)
        c.connect()
        self.assertEqual(c.hostname, 'xrv-ss-test1')

    def test_login_connect_connectReply(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxr --state connect_ssh'],
                       os='iosxr',
                       username='cisco',
                       line_password='admin',
                       enable_password='admin',
                       connect_reply=Dialog([[r'^(.*?)Connected.']]))
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRP/0/RP0/CPU0:Router#')
        self.assertIn("^(.*?)Connected.", str(c.connection_provider.get_connection_dialog()))
        c.disconnect()

    def test_connect_different_prompt_format(self):
        c = Connection(hostname='KLMER02-SU1', start=['mock_device_cli --os iosxr --state enable4'], os='iosxr')

        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRP/B0/CB0/CPU0:KLMER02-SU1#')
        c.disconnect()

    def test_connect_unresponsive(self):
        con = Connection(
                hostname='R1',
                os='iosxr',
                start=['mock_device_cli --os iosxr --state unresponsive_prompt --hostname R1'],
                credentials=dict(default=dict(username='admin', password='admin')))
        try:
            con.connect()
        finally:
            con.disconnect()

    def test_connect_ztp(self):
        c = Connection(hostname='Router',
                        start=['mock_device_cli --os iosxr --state spitfire_enable2'],
                        os='iosxr',
                        platform='spitfire',
                        enable_password='cisco',
                        init_exec_commands=[],
                        init_config_commands=[])
        try:
            c.connect()
        finally:
            c.disconnect()


class TestIosXRPluginExecute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxr --state enable'],
            os='iosxr',
        )
        cls.c.connect()

    def test_execute_error_pattern(self):
        with self.assertRaises(SubCommandFailure):
            self.c.execute('not a real command')

    def test_execute_error_pattern_negative(self):
        self.c.execute('not a real command partial')

    def test_execute_show_context(self):
        md = MockDeviceTcpWrapperIOSXR(port=0, state='enable')
        md.start()
        conn = Connection(hostname='Router',
                          start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
                          os='iosxr',
                          username='admin',
                          tacacs_password='admin')

        expected_output = '#0  0x00007f9b428c5aac\r\n#1  0x00007f9b428c5aac'

        try:
            conn.connect()
            out = conn.execute('show context')
            self.assertEqual(out, expected_output)
            conn.disconnect()
        finally:
            md.stop()

    def test_execute_avoid_state_detection_does_not_persist(self):
        md = MockDeviceTcpWrapperIOSXR(port=0, state='enable')
        md.start()
        conn = Connection(hostname='Router',
                          start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
                          os='iosxr',
                          username='admin',
                          tacacs_password='admin')

        try:
            conn.connect()
            conn.execute('show context')
            conn.execute('run', allow_state_change=True, timeout=5)
            self.assertEqual(conn.state_machine.current_state, 'run')
            conn.execute('exit', allow_state_change=True, timeout=5)
            self.assertEqual(conn.state_machine.current_state, 'enable')
        finally:
            conn.disconnect()
            md.stop()


class TestIosXrPluginPrompts(unittest.TestCase):
    """Tests for prompt handling."""
    def setUp(self):
        self._conn = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxr --state enable'],
            os='iosxr',
        )
        self._conn.connect()

    def test_confirm(self):
        """Check '\n' is sent in response to a [confirm] prompt."""
        self._conn.execute("process restart ifmgr location all")

    def test_confirm_y(self):
        """Check 'y\n' is sent in response to a [y/n] prompt."""
        self._conn.execute("clear logging")

    def test_y_on_repeat_confirm(self):
        self._conn.execute("clear logg")


class TestIosXrConfigPrompts(unittest.TestCase):
    """Tests for config prompt handling."""
    @classmethod
    def setUpClass(self):
        self._conn = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxr --state enable'],
            os='iosxr',
            mit=True,
            log_buffer=True
        )
        self._conn.connect()

    def test_failed_config(self):
        """Check that we can successfully return to an enable prompt after entering failed config."""
        self._conn.execute("configure terminal", allow_state_change=True)
        self._conn.execute("test failed")
        self._conn.spawn.timeout = 60
        self._conn.enable()

    def test_failed_config_error_message1(self):
        """Check that we can successfully return to an enable prompt after entering failed config."""
        with self.assertRaisesRegex(unicon.core.errors.SubCommandFailure, "% Invalid config"):
            self._conn.configure("test failed")

    def test_failed_config_error_message2(self):
        """Check that we can successfully return to an enable prompt after entering failed config."""
        with self.assertRaisesRegex(unicon.core.errors.SubCommandFailure, "% Invalid config"):
            self._conn.configure("test failed2")

    def test_update_hostname(self):
        self.assertEqual('Router', self._conn.hostname)
        self._conn.configure('hostname R2')
        self.assertEqual('R2', self._conn.hostname)

    def test_config_syslog(self):
        self._conn.execute('config_syslog', allow_state_change=True)
        self._conn.enable()


class TestIosXrPluginAdminService(unittest.TestCase):
    def test_admin(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable1'],
                          os='iosxr',
                          enable_password='cisco')

        with conn.admin_console() as console:
            out = console.execute('show platform')
            console.execute('clear configuration inconsistency')
            self.assertIn('IOS XR RUN', out)
        ret = conn.spawn.match.match_output
        self.assertIn('exit', ret)
        self.assertIn('Router#', ret)

    def test_admin_host(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable6'],
                          os='iosxr',
                          enable_password='cisco',
                          mit=True)

        conn.connect()
        with conn.admin_bash_console() as console:
            console.execute('ssh 10.0.2.16', allow_state_change=True)

class TestIosXrPluginBashService(unittest.TestCase):

    def test_bash(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable1'],
                          os='iosxr',
                          mit=True,
                          log_buffer=True)

        conn.connect()
        with conn.bash_console() as console:
            console.execute('cd ../common/')
            console.execute('cd ../disk0')
            out = console.execute('pwd')
            self.assertIn('disk0', out)
        ret = conn.spawn.match.match_output
        self.assertIn('exit', ret)
        self.assertIn('Router#', ret)
        conn.disconnect()

    def test_admin_bash(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable1'],
                          os='iosxr',
                          mit=True,
                          log_buffer=True)

        conn.connect()
        with conn.admin_bash_console() as console:
            console.execute('cd cisco_support/')
            out = console.execute('ls')
            self.assertIn('event_track', out)
        ret = conn.spawn.match.match_output
        self.assertIn('exit', ret)
        self.assertIn('Router#', ret)
        conn.disconnect()


    def test_bash2(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable2'],
                          os='iosxr',
                          mit=True,
                          log_buffer=True)

        conn.connect()
        with conn.bash_console() as console:
            out = console.execute('pwd')
            self.assertIn('disk0', out)
        ret = conn.spawn.match.match_output
        self.assertIn('exit', ret)
        self.assertIn('Router#', ret)
        conn.disconnect()


    def test_admin_bash2(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable2'],
                          os='iosxr',
                          mit=True,
                          log_buffer=True)

        conn.connect()
        with conn.admin_bash_console() as console:
            out = console.execute('pwd')
            self.assertIn('misc', out)
        ret = conn.spawn.match.match_output
        self.assertIn('exit', ret)
        self.assertIn('Router#', ret)
        conn.disconnect()

    def test_run_prompt_rsp(self):
        conn = Connection(hostname='R1',
                          start=['mock_device_cli --os iosxr --state enable_bash_run_prompt_rsp --hostname R1'],
                          os='iosxr',
                          mit=True,
                          log_buffer=True)

        conn.connect()
        with conn.bash_console():
            pass
        conn.disconnect()

    def test_run_prompt_rp(self):
        conn = Connection(hostname='R2',
                          start=['mock_device_cli --os iosxr --state enable_bash_run_prompt_rp --hostname R2'],
                          os='iosxr',
                          mit=True,
                          log_buffer=True)

        conn.connect()
        with conn.bash_console():
            pass
        conn.disconnect()

    def test_bash5(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable5'],
                          os='iosxr',
                          mit=True,
                          log_buffer=True)

        conn.connect()
        with conn.bash_console() as console:
            out = console.execute('pwd')
            self.assertIn('disk0', out)
        ret = conn.spawn.match.match_output
        self.assertIn('exit', ret)
        self.assertIn('Router#', ret)
        conn.disconnect()

    def test_admin_host_ios(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state bash_console7'],
                          os='iosxr',
                          mit=True,
                          log_buffer=True)

        conn.connect()
        try:
            conn.execute('run ssh 10.0.2.16', allow_state_change=True)
            self.assertEqual(conn.state_machine.current_state, 'admin_host')
        finally:
            conn.disconnect()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestIosXrPluginAdminConfigureService(unittest.TestCase):
    def test_admin_configure(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable1'],
                          os='iosxr',
                          enable_password='cisco')
        conn.connect()
        out = conn.admin_configure('show configuration')
        self.assertIn('% No configuration changes found.', out)
        self.assertEqual(conn.state_machine.current_state, 'enable')
        conn.disconnect()

    def test_admin_configure2(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable2'],
                          os='iosxr',
                          enable_password='cisco')
        conn.connect()
        out = conn.admin_configure('show configuration')
        self.assertIn('% No configuration changes found2.', out)
        self.assertEqual(conn.state_machine.current_state, 'enable')
        conn.disconnect()

    def test_admin_configure3(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable2'],
                          os='iosxr',
                          enable_password='cisco')
        conn.connect()
        out = conn.admin_configure('username root\nsecret 123\ngroup cisco-support\nexit')
        self.assertEqual(
            'username root\r\nRP/0/0/CPU0:secret 123\r\nRP/0/0/CPU0:group cisco-support\r\n'
            'RP/0/0/CPU0:exit\r\nRP/0/0/CPU0:commit\r\nRP/0/0/CPU0:', out)
        self.assertEqual(conn.state_machine.current_state, 'enable')
        conn.disconnect()

    def test_ha_admin_configure(self):
        md = MockDeviceTcpWrapperIOSXR(port=0, state='enable1,console_standby')
        md.start()
        conn = Connection(hostname='Router',
                          start=['telnet 127.0.0.1 {}'.format(md.ports[0]), 'telnet 127.0.0.1 {}'.format(md.ports[1])],
                          os='iosxr',
                          username='admin',
                          tacacs_password='admin')
        try:
            conn.connect()
            out = conn.admin_configure('show configuration')
            self.assertIn('% No configuration changes found.', out)
            self.assertEqual(conn.active.state_machine.current_state, 'enable')
            conn.disconnect()
        finally:
            md.stop()

    def test_ha_admin_configure2(self):
        md = MockDeviceTcpWrapperIOSXR(port=0, state='enable2,console_standby')
        md.start()
        conn = Connection(hostname='Router',
                          start=['telnet 127.0.0.1 {}'.format(md.ports[0]), 'telnet 127.0.0.1 {}'.format(md.ports[1])],
                          os='iosxr',
                          username='admin',
                          tacacs_password='admin')
        try:
            conn.connect()
            out = conn.admin_configure('show configuration')
            self.assertIn('% No configuration changes found2.', out)
            self.assertEqual(conn.active.state_machine.current_state, 'enable')
            conn.disconnect()
        finally:
            md.stop()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestIosXrPluginAdminExecuteService(unittest.TestCase):
    def test_admin_execute(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable1'],
                          os='iosxr',
                          enable_password='cisco')
        conn.connect()
        out = conn.admin_execute('pwd')
        self.assertIn('/misc/disk1', out)
        self.assertEqual(conn.state_machine.current_state, 'enable')
        conn.disconnect()

    def test_admin_configure2(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable2'],
                          os='iosxr',
                          enable_password='cisco')
        conn.connect()
        out = conn.admin_execute('pwd')
        self.assertIn('/misc/disk1:/admin', out)
        self.assertEqual(conn.state_machine.current_state, 'enable')
        conn.disconnect()

    def test_ha_admin_execute(self):
        md = MockDeviceTcpWrapperIOSXR(port=0, state='enable1,console_standby')
        md.start()
        conn = Connection(hostname='Router',
                          start=['telnet 127.0.0.1 {}'.format(md.ports[0]), 'telnet 127.0.0.1 {}'.format(md.ports[1])],
                          os='iosxr',
                          username='admin',
                          tacacs_password='admin')
        conn.connect()
        out = conn.admin_execute('pwd')
        self.assertIn('/misc/disk1', out)
        self.assertEqual(conn.active.state_machine.current_state, 'enable')
        conn.disconnect()
        md.stop()

    def test_ha_admin_execute2(self):
        md = MockDeviceTcpWrapperIOSXR(port=0, state='enable2,console_standby')
        md.start()
        conn = Connection(hostname='Router',
                          start=['telnet 127.0.0.1 {}'.format(md.ports[0]), 'telnet 127.0.0.1 {}'.format(md.ports[1])],
                          os='iosxr',
                          username='admin',
                          tacacs_password='admin')
        conn.connect()
        out = conn.admin_execute('pwd')
        self.assertIn('/misc/disk1:/admin', out)
        self.assertEqual(conn.active.state_machine.current_state, 'enable')
        conn.disconnect()
        md.stop()


class TestIosXrPluginAttachConsoleService(unittest.TestCase):
    def test_attach_console(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable1'],
                          os='iosxr',
                          enable_password='cisco')

        with conn.attach_console('0/RP0/CPU0') as console:
            out = console.execute('ls')
            self.assertIn('cmdline', out)
        ret = conn.spawn.match.match_output
        self.assertIn('exit', ret)
        self.assertIn('Router#', ret)

    def test_admin_attach_console(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable1'],
                          os='iosxr',
                          enable_password='cisco')

        with conn.admin_attach_console('0/RP0') as console:
            out = console.execute('pwd')
            self.assertIn('/misc/disk1', out)
        ret = conn.spawn.match.match_output
        self.assertIn('exit', ret)
        self.assertIn('Router#', ret)

    def test_admin_attach_console_error(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable1'],
                          os='iosxr',
                          enable_password='cisco')
        with self.assertRaises(SubCommandFailure):
            with conn.admin_attach_console('0/abc', timeout=5) as console:
                console.execute('pwd', timeout=8)


class TestIosxrConfigCommitCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperIOSXR(port=0, state='enable')
        cls.md.start()
        cls.md1 = MockDeviceTcpWrapperIOSXR(port=0, state='login,console_standby')
        cls.md1.start()
        cls.conn = Connection(hostname='Router', start=['telnet 127.0.0.1 {}'.format(cls.md.ports[0])], os='iosxr')
        cls.ha_dev = Connection(hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(cls.md1.ports[0]), 'telnet 127.0.0.1 {}'.format(cls.md1.ports[1])],
            username='admin',
            tacacs_password='admin',
            os='iosxr')
        cls.ha_dev.connect()
        cls.conn.connect()

    @classmethod
    def tearDownClass(cls):
        cls.conn.disconnect()
        cls.ha_dev.disconnect()
        cls.md1.stop()
        cls.md.stop()

    def test_config_commit(self):
        self.conn.configure('no logging console')
        self.ha_dev.configure('no logging console')
        self.assertEqual(self.conn.configure.commit_cmd, 'commit')
        self.assertEqual(self.ha_dev.configure.commit_cmd, 'commit')

    def test_config_commit_replace(self):
        self.conn.configure('no logging console', replace=True)
        self.ha_dev.configure('no logging console', replace=True)
        self.assertEqual(self.conn.configure.commit_cmd, 'commit replace')
        self.assertEqual(self.ha_dev.configure.commit_cmd, 'commit replace')

    def test_config_commit_best_effort(self):
        self.conn.configure('no logging console', best_effort=True)
        self.ha_dev.configure('no logging console', best_effort=True)
        self.assertEqual(self.conn.configure.commit_cmd, 'commit best-effort')
        self.assertEqual(self.ha_dev.configure.commit_cmd, 'commit best-effort')

    def test_config_commit_force(self):
        self.conn.configure('no logging console', force=True)
        self.ha_dev.configure('no logging console', force=True)
        self.assertEqual(self.conn.configure.commit_cmd, 'commit force')
        self.assertEqual(self.ha_dev.configure.commit_cmd, 'commit force')

    def test_bulk_config_commit(self):
        self.conn.configure(['no logging console'] * 2, bulk=True)
        self.ha_dev.configure(['no logging console'] * 2, bulk=True)
        self.assertEqual(self.conn.configure.commit_cmd, 'commit')
        self.assertEqual(self.ha_dev.configure.commit_cmd, 'commit')

    def test_bulk_config_commit_replace(self):
        self.conn.configure(['no logging console'] * 2, replace=True, bulk=True)
        self.ha_dev.configure(['no logging console'] * 2, replace=True, bulk=True)
        self.assertEqual(self.conn.configure.commit_cmd, 'commit replace')
        self.assertEqual(self.ha_dev.configure.commit_cmd, 'commit replace')

    def test_bulk_config_commit_force(self):
        self.conn.configure(['no logging console'] * 2, force=True, bulk=True)
        self.ha_dev.configure(['no logging console'] * 2, force=True, bulk=True)
        self.assertEqual(self.conn.configure.commit_cmd, 'commit force')
        self.assertEqual(self.ha_dev.configure.commit_cmd, 'commit force')


class TestIosxrConfigLockRetry(unittest.TestCase):

    transaction_lock_context_keys = (
        'config_transaction_locked',
        'config_transaction_lock_output',
        'config_transaction_lock_timeout',
    )

    def _assert_transaction_context_clean(self, context=None):
        context = self.conn.context if context is None else context
        for key in self.transaction_lock_context_keys:
            self.assertNotIn(key, context)

    def _connect(self, state='config_lock_enable'):
        self.md = MockDeviceTcpWrapperIOSXR(port=0, state=state)
        self.md.start()
        self.conn = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(self.md.ports[0])],
            os='iosxr',
            init_exec_commands=[],
            init_config_commands=[])
        self.conn.connect()
        self.conn.settings.CONFIG_LOCK_RETRY_SLEEP = 0

    def _connect_ha(self, state, peer_state='console_standby'):
        self.md = MockDeviceTcpWrapperIOSXR(
            port=0, state='{},{}'.format(state, peer_state))
        self.md.start()
        self.conn = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(self.md.ports[0]),
                   'telnet 127.0.0.1 {}'.format(self.md.ports[1])],
            credentials={
                'default': {
                    'username': 'admin',
                    'password': 'admin'}},
            os='iosxr',
            init_exec_commands=[],
            init_config_commands=[])
        self.conn.connect()
        self.conn.settings.CONFIG_LOCK_RETRY_SLEEP = 0

    def _test_config_lock_retry_commit(self, commit_command, **kwargs):
        self._connect()

        with patch.object(
                self.conn.spawn, 'sendline',
                wraps=self.conn.spawn.sendline) as sendline:
            self.conn.configure(
                'interface Loopback100', lock_retries=2, **kwargs)

        sent_commands = [call.args[0] for call in sendline.call_args_list]
        self.assertEqual(sent_commands.count(commit_command), 2)
        self.assertEqual(sent_commands.count('abort'), 1)
        self.assertEqual(self.conn.state_machine.current_state, 'enable')

    def tearDown(self):
        if hasattr(self, 'conn'):
            self.conn.disconnect()
        if hasattr(self, 'md'):
            self.md.stop()

    def test_config_lock_retries_complete_transaction(self):
        self._connect()
        commands = ['interface Loopback100',
                    'description config lock test']

        with patch.object(
                self.conn.spawn, 'sendline',
                wraps=self.conn.spawn.sendline) as sendline, \
                patch.object(
                    self.conn.spawn, 'expect',
                    wraps=self.conn.spawn.expect) as expect:
            output = self.conn.configure(
                commands, lock_retries=2, timeout=7)

        sent_commands = [call.args[0] for call in sendline.call_args_list]
        for command in commands:
            self.assertEqual(sent_commands.count(command), 2)
        self.assertEqual(sent_commands.count('commit'), 2)
        self.assertEqual(sent_commands.count('abort'), 1)
        self.assertEqual(
            sent_commands.count('show configuration commit changes last 1'),
            1)
        self.assertEqual(sent_commands.count('show configuration lock'), 2)
        self.assertNotIn('Failed to commit', output)
        self.assertIn('description config lock test', output)
        self.assertEqual(self.conn.state_machine.current_state, 'enable')
        self._assert_transaction_context_clean()
        expect_calls = [
            (call.args[0], call.kwargs.get('timeout'))
            for call in expect.call_args_list]
        iosxr_patterns = IOSXRPatterns()
        self.assertIn(([iosxr_patterns.config_prompt], 7), expect_calls)
        self.assertIn(([
            iosxr_patterns.enable_prompt.replace('%N', 'Router')], 7),
            expect_calls)

        self.conn.configure('interface Loopback100')
        self._assert_transaction_context_clean()

    def test_config_lock_retry_restores_aborted_hostname(self):
        self._connect()

        with patch.object(
                self.conn.spawn, 'sendline',
                wraps=self.conn.spawn.sendline) as sendline:
            self.conn.configure('hostname R2', lock_retries=2)

        sent_commands = [call.args[0] for call in sendline.call_args_list]
        self.assertEqual(sent_commands.count('hostname R2'), 2)
        self.assertEqual(sent_commands.count('commit'), 2)
        self.assertEqual(sent_commands.count('abort'), 1)
        self.assertEqual(self.conn.hostname, 'R2')
        self.assertEqual(self.conn.state_machine.current_state, 'enable')
        self._assert_transaction_context_clean()

    def test_transaction_context_is_cleaned_before_lock_release(self):
        self._connect()
        service = self.conn.configure
        original_handler = service.transaction_lock_handler
        handler_done = threading.Event()
        release_handler = threading.Event()
        observer_started = threading.Event()
        observer_done = threading.Event()
        configure_errors = []
        observed_context = {}

        def blocking_handler(**kwargs):
            original_handler(**kwargs)
            handler_done.set()
            if not release_handler.wait(10):
                raise RuntimeError('test timed out waiting to release handler')

        def run_configure():
            try:
                self.conn.configure(
                    'interface Loopback100', lock_retries=2)
            except Exception as error:
                configure_errors.append(error)

        def observe_context_after_acquire():
            observer_started.set()
            self.conn.acquire()
            try:
                observed_context.update(self.conn.context)
            finally:
                self.conn.release()
                observer_done.set()

        with patch.object(
                service, 'transaction_lock_handler', blocking_handler):
            configure_thread = threading.Thread(target=run_configure)
            observer_thread = threading.Thread(
                target=observe_context_after_acquire)
            configure_thread.start()
            try:
                self.assertTrue(handler_done.wait(10))
                observer_thread.start()
                self.assertTrue(observer_started.wait(10))
                self.assertFalse(observer_done.wait(0.2))
            finally:
                release_handler.set()
                configure_thread.join(20)
                if observer_thread.ident is not None:
                    observer_thread.join(20)

        self.assertFalse(configure_thread.is_alive())
        self.assertFalse(observer_thread.is_alive())
        self.assertFalse(configure_errors)
        self._assert_transaction_context_clean(observed_context)

    def test_transaction_context_cleanup_on_handler_exception(self):
        self._connect()
        service = self.conn.configure

        def failing_handler(**kwargs):
            context = kwargs['context']
            context['config_transaction_locked'] = True
            context['config_transaction_lock_output'] += 'diagnostic output'
            raise RuntimeError('synthetic recovery failure')

        with patch.object(
                service, 'transaction_lock_handler', failing_handler):
            with self.assertRaisesRegex(
                    RuntimeError, 'synthetic recovery failure'):
                self.conn.configure(
                    'interface Loopback100', lock_retries=2)

        self._assert_transaction_context_clean()
        self.assertTrue(self.conn.acquire(block=False))
        self.conn.release()

    def test_config_lock_pattern(self):
        pattern = IOSXRPatterns().config_lock
        locked_output = dedent('''\
            Tue Jun 28 11:22:10.449 UTC
            Session Write Lock
            00000212-00245489-00000000
        ''')
        write_locked_output = dedent('''\
            Thu Sep  3 12:15:23.540 UTC
            Session Locks
            Write Lock
            00002000-00001b8c-00000000
        ''')
        reserve_locked_output = dedent('''\
            Thu Sep  3 12:15:25.593 UTC
            Session Locks
            Reserve lock
            00002000-00001b8c-00000000
        ''')
        session_rebase_locked_output = dedent('''\
            Thu Sep 10 04:28:33.549 UTC
            Session Rebase Lock
        ''')
        rebase_lock_identifier_output = dedent('''\
            Thu Sep 10 04:28:33.549 UTC
            lock_subtree/rebase_lock
        ''')
        unlocked_output = dedent('''\
            Tue Jun 28 11:22:10.449 UTC
            Configuration database is available
        ''')

        self.assertIsNotNone(re.search(pattern, locked_output, re.M))
        self.assertIsNotNone(re.search(
            pattern, write_locked_output, re.M))
        self.assertIsNotNone(re.search(
            pattern, reserve_locked_output, re.M))
        self.assertIsNotNone(re.search(
            pattern, session_rebase_locked_output, re.M))
        self.assertIsNotNone(re.search(
            pattern, rebase_lock_identifier_output, re.M))
        self.assertIsNone(re.search(pattern, unlocked_output, re.M))

    def test_config_transaction_lock_pattern(self):
        patterns = IOSXRPatterns()
        locked_output = dedent('''\
            % Failed to commit .. Another configuration session
            had a lock on the running configuration.
            RP/0/RP0/CPU0:Router(config-if)#
        ''')
        sysadmin_locked_output = dedent('''\
            Failed to commit one or more configuration items
            Another configuration session had a lock on the running
            configuration
            sysadmin-vm:0_RP0(config-system)#
        ''')
        admin_locked_output = dedent('''\
            Failed to commit one or more configuration items
            Another configuration session had a lock on the running
            configuration
            RP/0/RP0/CPU0:Router(admin-config)#
        ''')
        unrelated_failure = dedent('''\
            Failed to commit one or more configuration items
            The configuration contains semantic errors
            RP/0/RP0/CPU0:Router(config)#
        ''')
        unrelated_session_failure = dedent('''\
            Failed to commit one or more configuration items
            Another configuration session modified the candidate configuration
            RP/0/RP0/CPU0:Router(config)#
        ''')
        lock_text_without_commit_failure = dedent('''\
            Another configuration session had a lock on the running
            configuration
            RP/0/RP0/CPU0:Router(config)#
        ''')

        pattern = patterns.config_transaction_lock_message
        self.assertIsNotNone(re.search(pattern, locked_output, re.I))
        self.assertIsNotNone(re.search(
            pattern, sysadmin_locked_output, re.I))
        self.assertIsNotNone(re.search(
            pattern, admin_locked_output, re.I))
        self.assertIsNone(re.search(pattern, unrelated_failure, re.I))
        self.assertIsNone(re.search(
            pattern, unrelated_session_failure, re.I))
        self.assertIsNone(re.search(
            pattern, lock_text_without_commit_failure, re.I))

    def test_config_lock_cleanup_failure_is_actionable(self):
        locked_output = dedent('''\
            % Failed to commit .. Another configuration session
            had a lock on the running configuration.
            RP/0/RP0/CPU0:Router(config)#''')
        diagnostic_output = dedent('''\
            Configuration changes for commit 1000000007
            RP/0/RP0/CPU0:Router(config)#''')
        context = {'config_transaction_lock_timeout': 7}
        spawn = Mock()
        state_machine = Mock()
        states = {
            'config': SimpleNamespace(
                pattern=IOSXRPatterns().config_prompt),
            'enable': SimpleNamespace(
                pattern=IOSXRPatterns().enable_prompt),
        }
        state_machine.get_state.side_effect = states.__getitem__
        spawn.expect.side_effect = [
            SimpleNamespace(match_output=diagnostic_output),
            RuntimeError('enable prompt not reached'),
        ]

        with self.assertRaisesRegex(
                SubCommandFailure,
                'Configuration transaction lock recovery failed'):
            recover_config_transaction_lock(
                spawn=spawn,
                context=context,
                state_machine=state_machine,
                start_state='config',
                end_state='enable',
                initial_output=locked_output)

        self.assertIn(
            'Configuration changes for commit 1000000007',
            context['config_transaction_lock_output'])
        self.assertNotIn('config_transaction_locked', context)
        self.assertEqual(
            [call.args[0] for call in spawn.sendline.call_args_list],
            ['show configuration commit changes last 1', 'abort'])

    def test_config_lock_recovery_without_admin_state(self):
        locked_output = dedent('''\
            % Failed to commit .. Another configuration session
            had a lock on the running configuration.
            RP/0/RP0/CPU0:Router(config)#''')
        diagnostic_output = dedent('''\
            Configuration changes for commit 1000000008
            RP/0/RP0/CPU0:Router(config)#''')
        context = {'config_transaction_lock_timeout': 7}
        spawn = Mock()
        spawn.expect.side_effect = [
            SimpleNamespace(match_output=diagnostic_output),
            SimpleNamespace(match_output='RP/0/RP0/CPU0:Router#'),
        ]
        state_machine = Mock()
        states = {
            'config': SimpleNamespace(
                pattern=IOSXRPatterns().config_prompt),
            'enable': SimpleNamespace(
                pattern=IOSXRPatterns().enable_prompt),
        }
        state_machine.get_state.side_effect = states.__getitem__

        recover_config_transaction_lock(
            spawn=spawn,
            context=context,
            state_machine=state_machine,
            start_state='config',
            end_state='enable',
            initial_output=locked_output)

        self.assertTrue(context['config_transaction_locked'])
        self.assertIn(
            'Configuration changes for commit 1000000008',
            context['config_transaction_lock_output'])
        self.assertEqual(
            [call.args[0]
             for call in state_machine.get_state.call_args_list],
            ['config', 'enable'])
        self.assertEqual(
            [call.args[0] for call in spawn.sendline.call_args_list],
            ['show configuration commit changes last 1', 'abort'])

    def test_transaction_lock_detection_precedes_error_validation(self):
        self._connect()
        match_output = dedent('''\
            commit
            % Failed to commit .. Another configuration session
            had a lock on the running configuration.
            RP/0/RP0/CPU0:Router(config)#''')
        dialog = Mock()
        dialog.process.return_value = SimpleNamespace(
            match_output=match_output)
        service = self.conn.configure
        service.result = ''
        service.prompt_recovery = False
        service.result_check_per_command = True
        service.error_pattern = [r'%\s+Failed to commit']

        transaction_locked = service.process_dialog_on_handle(
            self.conn, dialog, timeout=7)

        self.assertTrue(transaction_locked)
        self.assertEqual(
            self.conn.context['config_transaction_lock_output'],
            match_output)

    def test_config_lock_retries_bulk_transaction(self):
        self._connect()
        commands = ['interface Loopback100',
                    'description config lock test']
        bulk_command = '\n'.join(
            commands + [self.conn.settings.BULK_CONFIG_END_INDICATOR])

        with patch.object(
                self.conn.spawn, 'sendline',
                wraps=self.conn.spawn.sendline) as sendline:
            self.conn.configure(commands, bulk=True, lock_retries=2)

        sent_commands = [call.args[0] for call in sendline.call_args_list]
        self.assertEqual(sent_commands.count(bulk_command), 2)
        self.assertEqual(sent_commands.count('commit'), 2)
        self.assertEqual(self.conn.state_machine.current_state, 'enable')

    def test_config_lock_retries_banner_transaction(self):
        self._connect()
        commands = ['banner motd ^', 'config lock test', '^']

        with patch.object(
                self.conn.spawn, 'sendline',
                wraps=self.conn.spawn.sendline) as sendline:
            self.conn.configure(commands, lock_retries=2)

        sent_commands = [call.args[0] for call in sendline.call_args_list]
        for command in commands:
            self.assertEqual(sent_commands.count(command), 2)
        self.assertEqual(sent_commands.count('commit'), 2)
        self.assertEqual(self.conn.state_machine.current_state, 'enable')

    def test_config_lock_retries_exclusive_transaction(self):
        self._connect()

        with patch.object(
                self.conn.spawn, 'sendline',
                wraps=self.conn.spawn.sendline) as sendline:
            self.conn.configure_exclusive(
                'interface Loopback100', lock_retries=2)

        sent_commands = [call.args[0] for call in sendline.call_args_list]
        self.assertEqual(sent_commands.count('configure exclusive'), 2)
        self.assertNotIn('configure terminal', sent_commands)
        self.assertEqual(sent_commands.count('interface Loopback100'), 2)
        self.assertEqual(sent_commands.count('commit'), 2)
        self.assertEqual(sent_commands.count('abort'), 1)
        self.assertEqual(self.conn.state_machine.current_state, 'enable')
        self._assert_transaction_context_clean()

    def test_config_lock_retries_commit_force(self):
        self._test_config_lock_retry_commit('commit force', force=True)

    def test_config_lock_retries_commit_replace(self):
        self._test_config_lock_retry_commit('commit replace', replace=True)

    def test_config_lock_retries_commit_best_effort(self):
        self._test_config_lock_retry_commit(
            'commit best-effort', best_effort=True)

    def test_config_lock_retry_exhaustion_reports_details(self):
        self._connect('config_lock_persistent_enable')

        with patch.object(
                self.conn.spawn, 'sendline',
                wraps=self.conn.spawn.sendline) as sendline:
            with self.assertRaisesRegex(
                    SubCommandFailure,
                    '00000212-00245489-00000000') as error:
                self.conn.configure(
                    'interface Loopback100', lock_retries=1)

        self.assertIn(
            'Configuration changes for commit 1000000002',
            str(error.exception))
        sent_commands = [call.args[0] for call in sendline.call_args_list]
        self.assertEqual(sent_commands.count('commit'), 1)
        self.assertEqual(sent_commands.count('abort'), 1)
        self.assertFalse(any(
            command.startswith('clear configuration lock')
            for command in sent_commands))
        self.assertEqual(self.conn.state_machine.current_state, 'enable')
        self._assert_transaction_context_clean()

    def test_config_lock_retry_exhaustion_after_repeated_race(self):
        self._connect('config_lock_repeated_enable')

        with patch.object(
                self.conn.spawn, 'sendline',
                wraps=self.conn.spawn.sendline) as sendline:
            with self.assertRaisesRegex(
                    SubCommandFailure,
                    'Configuration transaction failed after 1 lock retries'):
                self.conn.configure(
                    'interface Loopback100', lock_retries=1)

        sent_commands = [call.args[0] for call in sendline.call_args_list]
        self.assertEqual(sent_commands.count('commit'), 2)
        self.assertEqual(sent_commands.count('abort'), 2)
        self.assertEqual(sent_commands.count('show configuration lock'), 1)
        self.assertEqual(self.conn.state_machine.current_state, 'enable')

    def test_config_lock_retry_zero(self):
        self._connect('config_lock_repeated_enable')

        with patch.object(
                self.conn.spawn, 'sendline',
                wraps=self.conn.spawn.sendline) as sendline:
            with self.assertRaisesRegex(
                    SubCommandFailure,
                    'Configuration transaction failed after 0 lock retries'):
                self.conn.configure(
                    'interface Loopback100', lock_retries=0)

        sent_commands = [call.args[0] for call in sendline.call_args_list]
        self.assertEqual(sent_commands.count('commit'), 1)
        self.assertEqual(sent_commands.count('abort'), 1)
        self.assertNotIn('show configuration lock', sent_commands)
        self.assertEqual(self.conn.state_machine.current_state, 'enable')

    def test_admin_config_lock_retries_complete_transaction(self):
        self._connect('admin_config_lock_enable')

        with patch.object(
                self.conn.spawn, 'sendline',
                wraps=self.conn.spawn.sendline) as sendline:
            self.conn.admin_configure(
                'show configuration', lock_retries=2)

        sent_commands = [call.args[0] for call in sendline.call_args_list]
        self.assertEqual(sent_commands.count('show configuration'), 2)
        self.assertEqual(sent_commands.count('commit'), 2)
        self.assertEqual(sent_commands.count('abort'), 1)
        self.assertEqual(self.conn.state_machine.current_state, 'enable')
        self._assert_transaction_context_clean()

    def test_ha_config_lock_retries_active_transaction(self):
        self._connect_ha('config_lock_enable')
        commands = ['interface Loopback100',
                    'description config lock test']

        with patch.object(
                self.conn.active.spawn, 'sendline',
                wraps=self.conn.active.spawn.sendline) as sendline:
            self.conn.configure(
                commands,
                target='active', lock_retries=2)

        sent_commands = [call.args[0] for call in sendline.call_args_list]
        for command in commands:
            self.assertEqual(sent_commands.count(command), 2)
        self.assertEqual(sent_commands.count('commit'), 2)
        self.assertEqual(sent_commands.count('abort'), 1)
        self.assertEqual(
            self.conn.active.state_machine.current_state, 'enable')
        self._assert_transaction_context_clean(self.conn.active.context)

    def test_ha_config_lock_retries_standby_transaction(self):
        # When neither peer reports standby_locked, IOS XR designates the
        # second peer active and the first peer standby.  This leaves the
        # transaction-lock mock reachable through target='standby'.
        self._connect_ha('config_lock_enable', peer_state='enable')
        commands = ['interface Loopback100',
                    'description config lock test']

        with patch.object(
                self.conn.standby.spawn, 'sendline',
                wraps=self.conn.standby.spawn.sendline) as standby_sendline, \
                patch.object(
                    self.conn.active.spawn, 'sendline',
                    wraps=self.conn.active.spawn.sendline) as active_sendline:
            self.conn.configure(
                commands,
                target='standby', lock_retries=2)

        sent_commands = [
            call.args[0] for call in standby_sendline.call_args_list]
        self.assertEqual(sent_commands, [
            'configure terminal',
            *commands,
            'commit',
            'show configuration commit changes last 1',
            'abort',
            'show configuration lock',
            'show configuration lock',
            'configure terminal',
            *commands,
            'commit',
            'end',
        ])
        self.assertFalse(active_sendline.called)
        self.assertEqual(
            self.conn.standby.state_machine.current_state, 'enable')
        self._assert_transaction_context_clean(self.conn.standby.context)
        self._assert_transaction_context_clean(self.conn.active.context)

    def test_ha_admin_config_lock_retries_active_transaction(self):
        self._connect_ha('admin_config_lock_enable')

        with patch.object(
                self.conn.active.spawn, 'sendline',
                wraps=self.conn.active.spawn.sendline) as sendline:
            self.conn.admin_configure(
                'show configuration', target='active', lock_retries=2)

        sent_commands = [call.args[0] for call in sendline.call_args_list]
        self.assertEqual(sent_commands.count('show configuration'), 2)
        self.assertEqual(sent_commands.count('commit'), 2)
        self.assertEqual(sent_commands.count('abort'), 1)
        self.assertEqual(
            self.conn.active.state_machine.current_state, 'enable')
        self._assert_transaction_context_clean(self.conn.active.context)

    def test_ha_admin_config_lock_retries_standby_transaction(self):
        # Keep the transaction-lock mock on the handle selected as standby.
        self._connect_ha('admin_config_lock_enable', peer_state='enable')

        with patch.object(
                self.conn.standby.spawn, 'sendline',
                wraps=self.conn.standby.spawn.sendline) as standby_sendline, \
                patch.object(
                    self.conn.active.spawn, 'sendline',
                    wraps=self.conn.active.spawn.sendline) as active_sendline:
            self.conn.admin_configure(
                'show configuration', target='standby', lock_retries=2)

        sent_commands = [
            call.args[0] for call in standby_sendline.call_args_list]
        self.assertEqual(sent_commands, [
            'admin',
            'config',
            'show configuration',
            'commit',
            'show configuration commit changes last 1',
            'abort',
            'exit',
            'show configuration lock',
            'show configuration lock',
            'admin',
            'config',
            'show configuration',
            'commit',
            'exit',
            'exit',
        ])
        self.assertFalse(active_sendline.called)
        self.assertEqual(
            self.conn.standby.state_machine.current_state, 'enable')
        self._assert_transaction_context_clean(self.conn.standby.context)
        self._assert_transaction_context_clean(self.conn.active.context)


class TestIosxrConfigure(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperIOSXR(port=0, state='enable')
        cls.md.start()
        cls.md1 = MockDeviceTcpWrapperIOSXR(port=0, state='login,console_standby')
        cls.md1.start()
        cls.conn = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(cls.md.ports[0])],
            os='iosxr')
        cls.ha_dev = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(cls.md1.ports[0]), 'telnet 127.0.0.1 {}'.format(cls.md1.ports[1])],
            username='admin',
            tacacs_password='admin',
            os='iosxr')
        cls.ha_dev.connect()
        cls.conn.connect()

    @classmethod
    def tearDownClass(cls):
        cls.conn.disconnect()
        cls.ha_dev.disconnect()
        cls.md1.stop()
        cls.md.stop()

    def test_configure_error_pattern(self):
        with self.assertRaises(SubCommandFailure):
            self.conn.configure('test failed')
        with self.assertRaises(SubCommandFailure):
            self.ha_dev.configure('test failed')


class TestIosXRPluginPing(unittest.TestCase):
    def test_ping_fail_no_vrf(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxr --state enable'],
                       os='iosxr',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        with self.assertRaises(SubCommandFailure):
            c.ping('10.0.0.1')

    def test_ping_success_vrf(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxr --state enable'],
                       os='iosxr',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        r = c.ping('10.0.0.2', vrf='management')
        self.assertEqual(r.strip(), "\r\n".join("""ping vrf management 10.0.0.2
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.0.0.2, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/1/3 ms
RP/0/RP0/CPU0:""".splitlines()))  # noqa


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestIosXrPluginConfigureExclusiveService(unittest.TestCase):
    def test_configure_exclusive(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable'],
                          os='iosxr',
                          enable_password='cisco')
        conn.connect()
        out = conn.configure_exclusive('logging console disable')
        self.assertIn('logging console disable', out)
        self.assertEqual(conn.state_machine.current_state, 'enable')
        conn.disconnect()


class TestIosXrPluginReload(unittest.TestCase):

    def test_reload_ncs540(self):
        md = MockDeviceTcpWrapperIOSXR(hostname='R2', port=0, state='ncs540_enable')
        md.start()

        c = Connection(
            hostname='R2',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxr',
            settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
            credentials=dict(default=dict(username='cisco', password='cisco')),
            init_config_commands=[],
            mit=True,
            log_buffer=True
        )
        try:
            c.connect()
            c.settings.POST_RELOAD_WAIT = 1
            result = c.reload(return_output=True)
            self.assertGreater(len(result.output), 10)
        finally:
            c.disconnect()
            md.stop()

    def test_reload_wish_continue(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable7'],
                          os='iosxr',
                          enable_password='cisco',
                          mit=True,
                          settings=dict(POST_RELOAD_WAIT=1))
        try:
            conn.connect()
            conn.reload()
        finally:
            conn.disconnect()


class TestMorePrompt(unittest.TestCase):

    def test_more_prompt(self):
        c = Connection(
            hostname="Router",
            start=["mock_device_cli --os iosxr --state enable"],
            os="iosxr",
            init_exec_commands=[],
            init_config_commands=[],
            settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
        )
        c.connect()
        try:
            output = c.execute("show command with more")
            self.assertEqual(c.state_machine.current_state, "enable")
            self.assertEqual(output, ' \r\noutput1\r\n \r\noutput2' )
        finally:
            c.disconnect()


class TestXRMonitorCommand(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state enable'],
                          os='iosxr',
                          enable_password='cisco',
                          mit=True)
        cls.conn.connect()

    @classmethod
    def tearDownClass(cls):
        cls.conn.disconnect()

    def test_monitor_interface_iface(self):
        conn = self.conn
        output = None
        conn.monitor('interface eth0')
        o = conn.monitor('clear')
        self.assertEqual(o, "c\r\nBrief='b', Detail='d', Protocol(IPv4/IPv6)='r'")
        output = conn.monitor.stop()

        self.maxDiff = None

        self.assertEqual(output.replace('\r', '').strip(), dedent("""\
            monitor interface eth0
            R1                   Monitor Time: 00:00:02          SysUptime: 22:48:09

            FourHundredGigE0/0/0/2 is up, line protocol is up
            Encapsulation ARPA

            Traffic Stats:(2 second rates)                                     Delta
              Input  Packets:                      2733                            0

            Quit='q', Freeze='f', Thaw='t', Clear='c', Interface='i',
            Next='n', Prev='p'
            Brief='b', Detail='d', Protocol(IPv4/IPv6)='r'
            c
            Brief='b', Detail='d', Protocol(IPv4/IPv6)='r'
            q"""))

    def test_monitor_interface(self):
        conn = self.conn
        output = None
        conn.monitor('interface')
        output = conn.monitor.stop()
        self.assertEqual(output.replace('\r', '').strip(), dedent("""\
            monitor interface
            R1                   Monitor Time: 00:00:02          SysUptime: 22:48:09

            Quit='q',     Clear='c',    Freeze='f', Thaw='t',
            Next set='n', Prev set='p', Bytes='y',  Packets='k'
            (General='g', IPv4 Uni='4u', IPv4 Multi='4m', IPv6 Uni='6u', IPv6 Multi='6m')
            q"""))

    def test_monitor_not_supported(self):
        conn = self.conn
        with self.assertRaises(SubCommandFailure):
            conn.monitor('something else')

    def test_monitor_tail(self):
        conn = self.conn
        conn.monitor('interface')
        output = conn.monitor.tail(timeout=3)
        self.assertEqual(output.replace('\r', '').strip(), dedent("""\
            monitor interface
            R1                   Monitor Time: 00:00:02          SysUptime: 22:48:09

            Quit='q',     Clear='c',    Freeze='f', Thaw='t',
            Next set='n', Prev set='p', Bytes='y',  Packets='k'
            (General='g', IPv4 Uni='4u', IPv4 Multi='4m', IPv6 Uni='6u', IPv6 Multi='6m')"""))

    def test_monitor_general(self):
        conn = self.conn
        conn.monitor('interface')
        output = conn.monitor('next set')
        expected_output = "n\r\n(General='g', IPv4 Uni='4u', IPv4 Multi='4m', IPv6 Uni='6u', IPv6 Multi='6m')"
        self.assertEqual(output, expected_output)

        output = conn.monitor('general')
        expected_output = "g\r\n(General='g', IPv4 Uni='4u', IPv4 Multi='4m', IPv6 Uni='6u', IPv6 Multi='6m')"
        self.assertEqual(output, expected_output)

        output = conn.monitor('IPv4 Uni')
        expected_output = "4u\r\n(General='g', IPv4 Uni='4u', IPv4 Multi='4m', IPv6 Uni='6u', IPv6 Multi='6m')"
        self.assertEqual(output, expected_output)

        output = conn.monitor('ipv4uni')
        expected_output = "4u\r\n(General='g', IPv4 Uni='4u', IPv4 Multi='4m', IPv6 Uni='6u', IPv6 Multi='6m')"
        self.assertEqual(output, expected_output)

    def test_monitor_start_state(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state monitor_interface'],
                          os='iosxr',
                          mit=True)

        try:
            conn.connect()
            conn.execute('show platform')
        finally:
            self.assertEqual(conn.state_machine.current_state, 'enable')
            conn.disconnect()

    def test_monitor_stop_timeout(self):
        conn = Connection(hostname='Router',
                          start=['mock_device_cli --os iosxr --state monitor_interface_slow_stop'],
                          os='iosxr',
                          mit=True)

        try:
            conn.connect()
            conn.monitor.stop()
        finally:
            self.assertEqual(conn.state_machine.current_state, 'enable')
            conn.disconnect()

    def test_monitor_prompt_regex(self):
        p = IOSXRPatterns().monitor_command_pattern
        output = MockDeviceIOSXR(state="enable").mock_data["monitor_interface"]["preface"]
        matches = re.findall(p, output)
        self.assertEqual(
            matches,
            [
                ("Quit", "q"),
                ("Clear", "c"),
                ("Freeze", "f"),
                ("Thaw", "t"),
                ("Next set", "n"),
                ("Prev set", "p"),
                ("Bytes", "y"),
                ("Packets", "k"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
