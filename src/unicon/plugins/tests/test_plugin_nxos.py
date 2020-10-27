"""
Unittests for NXOS plugin

Uses the unicon.plugins.tests.mock.mock_device_ios script to test NXOS plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import os
import yaml
import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure, StateMachineError, \
    ConnectionError
from unicon.plugins.tests.mock.mock_device_nxos import MockDeviceTcpWrapperNXOS
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'nxos/nxos_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestNxosPluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='switch',
                        start=['mock_device_cli --os nxos --state exec'],
                        os='nxos',
                        username='cisco',
                        tacacs_password='cisco')
        c.connect()
        assert c.spawn.match.match_output == 'end\r\nswitch# '

    def test_login_kerberos(self):
        c = Connection(hostname='switch',
                        start=['mock_device_cli --os nxos --state username_kerberos'],
                        os='nxos',
                        username='cisco',
                        tacacs_password='cisco')
        c.connect()
        assert c.spawn.match.match_output == 'end\r\nswitch# '

    def test_login_connect_connectReply(self):
        c = Connection(hostname='switch',
                        start=['mock_device_cli --os nxos --state exec'],
                        os='nxos',
                        username='cisco',
                        tacacs_password='cisco',
                        connect_reply = Dialog([[r'^(.*?)Password:']]))
        c.connect()
        self.assertIn("^(.*?)Password:", str(c.connection_provider.get_connection_dialog()))
        c.disconnect()

class TestNxosPluginShellexec(unittest.TestCase):

    def test_shellexec(self):
        c = Connection(hostname='switch',
                        start=['mock_device_cli --os nxos --state exec'],
                        os='nxos',
                        username='cisco',
                        tacacs_password='cisco')

        output = c.shellexec(['sudo yum list installed | grep n9000'])
        assert output == "\r\n".join("""\
sudo yum list installed | grep n9000
base-files.n9000                        3.0.14-r74.2                   installed
bfd.lib32_n9000                         1.0.0-r0                       installed
bash-4.2$""".splitlines())

        assert c.spawn.match.match_output == 'exit\r\nswitch# '

class TestNxosN3KPluginShellexec(unittest.TestCase):

    def test_shellexec_n3k(self):
        c = Connection(hostname='switch',
                        start=['mock_device_cli --os nxos --state exec_n3k'],
                        os='nxos',
                        series='n3k',
                        username='cisco',
                        tacacs_password='cisco')
        c.shellexec(['ls'])
        assert c.spawn.match.match_output == 'exit\r\nswitch# '


class TestNxosPluginBashService(unittest.TestCase):

    def test_bash(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os nxos --state exec'],
                       os='nxos',
                       username='cisco',
                       tacacs_password='cisco')

        with c.bash_console() as console:
            console.execute('ls')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('switch#', c.spawn.match.match_output)

    def test_bash_ha(self):
        c = Connection(hostname='switch',
                        start=['mock_device_cli --os nxos --state exec',
                               'mock_device_cli --os nxos --state exec'],
                        os='nxos',
                        username='cisco',
                        tacacs_password='cisco')
        with c.bash_console() as console:
            console.execute('ls')
        self.assertIn('exit', c.active.spawn.match.match_output)
        self.assertIn('switch#', c.active.spawn.match.match_output)

    def test_bash_ha_standby(self):
        ha = MockDeviceTcpWrapperNXOS(port=0, state='exec,nxos_exec_standby')
        ha.start()
        c = Connection(hostname='switch',
                        start=['telnet 127.0.0.1 '+  str(ha.ports[0]), 'telnet 127.0.0.1 '+ str(ha.ports[1]) ],
                       os='nxos', username='cisco', tacacs_password='cisco')
        try:
            c.connect()
            with c.bash_console(target='standby') as console:
                console.execute('ls', target='standby')
            self.assertIn('exit', c.standby.spawn.match.match_output)
            self.assertIn('switch(standby)#', c.standby.spawn.match.match_output)
            c.disconnect()
        finally:
            ha.stop()


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestNxosPluginGuestshellService(unittest.TestCase):

    def test_guestshell_basic(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os nxos --state exec'],
                       os='nxos',
                       username='cisco',
                       tacacs_password='cisco')

        with c.guestshell() as gs:
            output = gs.execute('pwd')
        self.assertEqual('/home/admin', output)
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('switch#', c.spawn.match.match_output)

    def test_guestshell_enable(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os nxos --state exec'],
                       os='nxos',
                       username='cisco',
                       tacacs_password='cisco')

        with c.guestshell(enable_guestshell=True, retries=5) as gs:
            gs.execute('pwd')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('switch#', c.spawn.match.match_output)

        # Attempt to activate again - guestshell is already active
        with c.guestshell(enable_guestshell=True, retries=5) as gs:
            gs.execute('pwd')

    def test_guestshell_retries_exceeded_enable(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os nxos --state exec'],
                       os='nxos',
                       username='cisco',
                       tacacs_password='cisco')

        with self.assertRaises(SubCommandFailure) as err:
            with c.guestshell(enable_guestshell=True, retries=2) as gs:
                gs.execute("pwd")
        self.assertEqual("Failed to enable guestshell after 2 tries",
                         str(err.exception))

    def test_guestshell_retries_exceeded_activate(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os nxos --state exec'],
                       os='nxos',
                       username='cisco',
                       tacacs_password='cisco')

        with self.assertRaises(SubCommandFailure) as err:
            with c.guestshell(enable_guestshell=True, retries=3) as gs:
                gs.execute("pwd")
        self.assertEqual("Guestshell failed to become activated after 3 tries",
                         str(err.exception))

    def test_ha_guestshell_basic(self):
        ha = MockDeviceTcpWrapperNXOS(port=0, state='exec,nxos_exec_standby', hostname='switch')
        ha.start()
        d = Connection(hostname='switch',
                       start=['telnet 127.0.0.1 ' + str(ha.ports[0]),
                              'telnet 127.0.0.1 ' + str(ha.ports[1])],
                       os='nxos',
                       username='cisco',
                       tacacs_password='cisco')
        try:
            d.connect()
            with d.guestshell() as gs:
                output = gs.execute('pwd')
            self.assertEqual('/home/admin', output)
            self.assertIn('exit', d.active.spawn.match.match_output)
            self.assertIn('switch#', d.active.spawn.match.match_output)
            d.disconnect()
        finally:
            ha.stop()


class TestNxosPluginAttachConsoleService(unittest.TestCase):

    def test_shell(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os nxos --state exec'],
                       os='nxos',
                       username='cisco',
                       tacacs_password='cisco')

        with c.attach_console(1) as console:
            console.execute('ls')


class TestNxosPluginPing6Service(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.d = Connection(hostname='switch',
                            start=['mock_device_cli --os nxos --state exec'],
                            os='nxos',
                            username='cisco',
                            tacacs_password='cisco')
        cls.d.connect()
        cls.ha = MockDeviceTcpWrapperNXOS(port=0, state='exec,nxos_exec_standby')
        cls.ha.start()
        cls.ha_device = Connection(hostname='switch',
                                    start=['telnet 127.0.0.1 '+  str(cls.ha.ports[0]), 'telnet 127.0.0.1 '+ str(cls.ha.ports[1]) ],
                                    os='nxos', username='cisco', tacacs_password='cisco')
        cls.ha_device.connect()

    @classmethod
    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def tearDownClass(cls):
        cls.d.disconnect()
        cls.ha_device.disconnect()
        cls.ha.stop()

    def test_ha_ping6(self):
        try:
            self.ha_device.ping6(addr="2003::7010", vrf="management")
            result = True
        except Exception as e:
            print('Error in ping6 service for dual rp: {}'.format(e))
            result = False
        self.assertTrue(result)

    def test_single_rp_ping6(self):
        try:
            self.d.ping6(addr="2003::7010", vrf="management")
            result = True
        except Exception as e:
            print('Error in ping6 service for single rp: {}'.format(e))
            result = False
        self.assertTrue(result)


class TestNxosPluginExecute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='switch',
                        start=['mock_device_cli --os nxos --state exec'],
                        os='nxos',
                        username='cisco',
                        tacacs_password='cisco',
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        cls.c.connect()

    def test_execute_show_feature(self):
        cmd = 'show feature'
        expected_response = mock_data['exec']['commands'][cmd].strip()
        r = self.c.execute(cmd).replace('\r', '')
        self.assertEqual(r, expected_response)

    def test_execute_error_pattern(self):
        with self.assertRaises(SubCommandFailure) as err:
          r = self.c.execute('not a real command')

    def test_execute_error_pattern_negative(self):
        r = self.c.execute('not a real command partial')

    def test_execute_copy_not_allowed(self):
        with self.assertRaises(SubCommandFailure):
            self.c.execute('copy sftp://server/root/nxos.7.0.3.I7.8.bin bootflash:///nxos.7.0.3.I7.8.bin vrf management')

        with self.assertRaises(SubCommandFailure):
            self.c.execute('copy scp://localhost/nxos.7.0.3.I7.8.bin bootflash:///nxos.7.0.3.I7.8.bin vrf management')


class TestNxosCrash(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='switch',
                        start=['mock_device_cli --os nxos --state exec'],
                        os='nxos',
                        username='cisco',
                        tacacs_password='cisco',
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        cls.c.connect()

    @classmethod
    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def tearDownClass(cls):
        cls.c.execute('boot', allow_state_change=True)
        cls.c.disconnect()

    def test_execute_crash(self):
        self.c.enable()
        with self.assertRaises(StateMachineError) as e1:
            self.c.execute('crash command')
        self.assertEqual(self.c.state_machine.current_state, 'loader')


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestNxosPluginReloadService(unittest.TestCase):

    def test_reload_config_lock_retries_succeed_with_default(self):
        dev = Connection(
            hostname='N93_1',
            start=['mock_device_cli --os nxos --state login2'],
            os='nxos',
            username='cisco',
            tacacs_password='cisco',
            enable_password='cisco',
        )
        dev.connect()
        dev.start = ['mock_device_cli --os nxos --state reconnect_login']
        dev.reload()
        dev.configure('no logging console')
        dev.disconnect()

    def test_reload_config_lock_retries_succeed(self):
        dev = Connection(
            hostname='N93_1',
            start=['mock_device_cli --os nxos --state login2'],
            os='nxos',
            username='cisco',
            tacacs_password='cisco',
            enable_password='cisco',
        )
        dev.connect()
        dev.start = ['mock_device_cli --os nxos --state reconnect_login']
        dev.reload(config_lock_retries=2, config_lock_retry_sleep=1)
        dev.configure('no logging console')
        dev.disconnect()

    def test_reload_config_lock_retries_fail(self):
        dev = Connection(
            hostname='N93_1',
            start=['mock_device_cli --os nxos --state login2'],
            os='nxos',
            username='cisco',
            tacacs_password='cisco',
            enable_password='cisco',
        )
        dev.connect()
        dev.start = ['mock_device_cli --os nxos --state reconnect_login']
        with self.assertRaises(ConnectionError):
            dev.reload(config_lock_retries=1, config_lock_retry_sleep=1)


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestNxosPluginMaintenanceMode(unittest.TestCase):

    def test_maint_mode(self):
        dev = Connection(
            hostname='N93_1',
            start=['mock_device_cli --os nxos --state exec_maint'],
            os='nxos',
            credentials={
                'defaut': {
                    'username': 'cisco',
                    'password': 'cisco'
                }
            }
        )
        dev.connect()
        dev.disconnect()


class TestNxosIncorrectLogin(unittest.TestCase):

    def test_incorrect_login(self):
        dev = Connection(
            hostname='switch',
            start=['mock_device_cli --os nxos --state password4'],
            os='nxos',
            credentials={
                'default': {
                    'username': 'admin',
                    'password': 'cisco'
                }
            }
        )
        dev.connect()
        dev.disconnect()


class TestNxosPluginConfigure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = Connection(hostname='switch',
                        start=['mock_device_cli --os nxos --state exec'],
                        os='nxos',
                        username='cisco',
                        tacacs_password='cisco',
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        cls.dev.connect()

    def test_execute_configure_commit(self):
        acl_cfg = "configure session acl6\nip access-list acl6\n"\
            "10 permit ip 63.1.1.1/24 64.1.1.1/24\nip access-list acl5\n10 permit ip 130.1.1.1/24 140.1.1.1/24"

        out = self.dev.configure(acl_cfg, commit=True)

        self.assertIn('Commit Successful', out)


if __name__ == "__main__":
    unittest.main()
