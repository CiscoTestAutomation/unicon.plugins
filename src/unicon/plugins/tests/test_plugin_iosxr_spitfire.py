"""
Unittests for IOSXR/SPITFIRE plugin

Uses the mock_device.py script to test IOSXR plugin.

"""

__author__ = "Sritej K V R <skanakad@cisco.com>"

import os
import unittest
from unittest.mock import patch, Mock, call

from pyats.topology import loader

import unicon
from unicon import Connection
from unicon.plugins.tests.mock.mock_device_iosxr_spitfire import MockDeviceTcpWrapperSpitfire
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path
import unicon.plugins

patch.TEST_PREFIX = ('test', 'setUp', 'tearDown')

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXrSpitfirePluginDevice(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperSpitfire(port=0, state='spitfire_login')
        cls.md.start()

        cls.testbed = """
        devices:
          Router:
            os: iosxr
            platform: spitfire
            type: router
            tacacs:
                username: admin
            passwords:
                tacacs: lab
                enable: lab
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
        """.format(cls.md.ports[0])

    def test_connect(self):
        tb = loader.load(self.testbed)
        self.r = tb.devices.Router
        self.r.connect()
        self.assertEqual(self.r.is_connected(), True)
        self.r.disconnect()

    @classmethod
    def tearDownClass(cls):
        cls.md.stop()


class TestIosXrSpitfirePlugin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxr --state spitfire_login'],
            os='iosxr',
            platform='spitfire',
            credentials={'default': {
                'username': 'admin',
                'password': 'lab'
            }})

    def test_connect(self):
        self.c.connect()
        self.assertEqual(self.c.spawn.match.match_output,
                         'end\r\nRP/0/RP0/CPU0:Router#')

    def test_execute(self):
        r = self.c.execute('show platform')
        with open(
                os.path.join(mockdata_path,
                             'iosxr/spitfire/show_platform.txt'),
                'r') as outputfile:
            expected_device_output = outputfile.read().strip()
        device_output = r.replace('\r', '').strip()
        self.maxDiff = None
        self.assertEqual(device_output, expected_device_output)

    def test_reload(self):
        self.c.reload()

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()


class TestIosXrSpitfirePluginPrompts(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxr --state spitfire_enable'],
            os='iosxr',
            platform='spitfire',
            mit=True)
        cls.c.connect()

    def test_xr_bash_prompt(self):
        self.c.state_machine.go_to('xr_bash', self.c.spawn)
        self.assertEqual(self.c.spawn.match.match_output,
                         'bash\r\n[ios:/misc/scratch]$')
        self.c.state_machine.go_to('enable', self.c.spawn)
        self.assertEqual(self.c.spawn.match.match_output,
                         'exit\r\nRP/0/RP0/CPU0:Router#')

    def test_xr_run_prompt(self):
        self.c.state_machine.go_to('xr_run', self.c.spawn)
        self.assertEqual(self.c.spawn.match.match_output,
                         'run\r\n[node0_RP0_CPU0:~]$')
        self.c.state_machine.go_to('enable', self.c.spawn)
        self.assertEqual(self.c.spawn.match.match_output,
                         'exit\r\nRP/0/RP0/CPU0:Router#')

    def test_xr_env_prompt(self):
        self.c.state_machine.go_to('xr_env', self.c.spawn)
        self.assertEqual(self.c.spawn.match.match_output,
                         'xrenv\r\nXR[ios:~]$')
        self.c.state_machine.go_to('enable', self.c.spawn)
        self.assertEqual(self.c.spawn.match.match_output,
                         'exit\r\nRP/0/RP0/CPU0:Router#')

    def test_xr_config_prompt(self):
        self.c.state_machine.go_to('config', self.c.spawn)
        self.assertEqual(
            self.c.spawn.match.match_output,
            'configure terminal\r\nRP/0/RP0/CPU0:Router(config)#')
        self.c.state_machine.go_to('enable', self.c.spawn)
        self.assertEqual(self.c.spawn.match.match_output,
                         'end\r\nRP/0/RP0/CPU0:Router#')

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()


class TestIosXrSpitfirePluginSvcs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxr --state spitfire_enable'],
            os='iosxr',
            platform='spitfire',
            mit=True)
        cls.c.connect()

    def test_execute(self):
        self.c.enable()
        self.c.execute("bash", allow_state_change=True)
        self.assertEqual(self.c.spawn.match.match_output,
                         'bash\r\n[ios:/misc/scratch]$')

    def test_execute_2(self):
        self.c.enable()
        self.c.execute("bash", allow_state_change=True)
        self.c.execute("ls", allow_state_change=True)
        self.assertEqual(
            self.c.spawn.match.match_output,
            'ls\r\nakrhegde_15888571384782863_mppinband_rtr1.log  '
            'akrhegde_15888589016873305_mppinband_rtr1.log  asic-err-logs-backup  clihistory\r\n[ios:/misc/scratch]$'
        )

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()


class TestIosXrSpitfireHAConnect(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.md = MockDeviceTcpWrapperSpitfire(
            port=0, state='spitfire_login,spitfire_console_standby')

        cls.md.start()

        cls.testbed = """
        devices:
          Router:
            os: iosxr
            platform: spitfire
            type: router
            credentials:
              default:
                username: admin
                password: lab
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
              b:
                protocol: telnet
                ip: 127.0.0.1
                port: {}

        """.format(cls.md.ports[0], cls.md.ports[1])

        tb = loader.load(cls.testbed)
        cls.r = tb.devices.Router
        cls.r.connect(prompt_recovery=True)

    def test_connect(self):
        self.assertEqual(self.r.is_connected(), True)

    def test_handle(self):
        self.assertEqual(
            self.r.a.role,
            "active",
        )
        self.assertEqual(self.r.b.role, "standby")

    def test_reload(self):
        self.r.reload()

    def test_switchover(self):
        self.r.switchover(sync_standby=False)

    def test_switchover_with_sync(self):
        self.r.switchover(sync_standby=True)

    @classmethod
    def tearDown(cls):
        cls.r.disconnect()
        cls.md.stop()


class TestIosXrSpitfirePluginConnectReply(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxr --state spitfire_enable'],
            os='iosxr',
            platform='spitfire',
            username='admin',
            enable_password='lab',
            connect_reply=Dialog([[r'^(.*?)Password:']]))
        cls.c.connect()

    def test_connection_connectReply(self):
        self.assertIn("^(.*?)Password:",
                      str(self.c.connection_provider.get_connection_dialog()))

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()


@patch.object(unicon.plugins.iosxr.spitfire.settings.SpitfireSettings,
              'CONFIG_LOCK_TIMEOUT', 5)
class TestIosXrSpitfirePluginConnectConfigLock(unittest.TestCase):

    def test_configlocktimeout(self):
        self.md = MockDeviceTcpWrapperSpitfire(port=0, state='spitfire_login')
        self.md.start()

        self.testbed = """
        devices:
          Router:
            os: iosxr
            platform: spitfire
            type: router
            tacacs:
                username: admin
            passwords:
                tacacs: lab
                enable: lab
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
        """.format(self.md.ports[0])
        tb = loader.load(self.testbed)
        self.r = tb.devices.Router

        try:
            self.r.connect(prompt_recovery=True)
        except Exception:
            connect_fail = True

        self.assertTrue(connect_fail, "Connection failed ")

    def test_configindefinitelock(self):
        self.md = MockDeviceTcpWrapperSpitfire(
            port=0, state='spitfire_enable_config_lock')
        self.md.start()

        self.testbed = """
        devices:
          Router:
            os: iosxr
            platform: spitfire
            type: router
            tacacs:
                username: admin
            passwords:
                tacacs: lab
                enable: lab
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
        """.format(self.md.ports[0])
        tb = loader.load(self.testbed)
        self.r = tb.devices.Router

        try:
            self.r.connect(prompt_recovery=True)
        except Exception:
            connect_fail = True

        self.assertTrue(connect_fail, "Connection failed ")

    def test_configztplock(self):
        self.md = MockDeviceTcpWrapperSpitfire(
            port=0, state='spitfire_enable_ztp_lock')
        self.md.start()

        self.testbed = """
        devices:
          Router:
            os: iosxr
            platform: spitfire
            type: router
            tacacs:
                username: admin
            passwords:
                tacacs: lab
                enable: lab
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
        """.format(self.md.ports[0])
        tb = loader.load(self.testbed)
        self.r = tb.devices.Router

        try:
            self.r.connect(prompt_recovery=True)
        except Exception:
            connect_fail = True

        self.assertTrue(connect_fail, "Connection failed ")

    def tearDown(self):
        self.r.disconnect()
        self.md.stop()


class TestIosXrSpitfirePluginSwitchTo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxr --state spitfire_enable'],
            os='iosxr',
            platform='spitfire',
            mit=True)

        cls.c.connect()

    def test_switchto(self):
        self.c.switchto("config")
        self.assertEqual(
            self.c.spawn.match.match_output,
            'configure terminal\r\nRP/0/RP0/CPU0:Router(config)#')
        self.c.switchto('enable')
        self.assertEqual(self.c.spawn.match.match_output,
                         'end\r\nRP/0/RP0/CPU0:Router#')

    def test_switchto_xr_env(self):
        self.c.switchto("xr_run")
        self.assertEqual(self.c.spawn.match.match_output,
                         'run\r\n[node0_RP0_CPU0:~]$')
        self.c.switchto("xr_env")
        self.assertEqual(self.c.spawn.match.match_output,
                         'xrenv\r\nXR[ios:~]$')
        self.c.switchto('enable')
        self.assertEqual(self.c.spawn.match.match_output,
                         'exit\r\nRP/0/RP0/CPU0:Router#')
        self.c.switchto("xr_bash")
        self.assertEqual(self.c.spawn.match.match_output,
                         'bash\r\n[ios:/misc/scratch]$')
        self.c.switchto("xr_env")
        self.assertEqual(self.c.spawn.match.match_output,
                         'xrenv\r\nXR[ios:~]$')
        self.c.switchto('enable')
        self.assertEqual(self.c.spawn.match.match_output,
                         'exit\r\nRP/0/RP0/CPU0:Router#')

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()


class TestIosXrSpitfirePluginAttachConsoleService(unittest.TestCase):

    def test_attach_console_rp0(self):
        conn = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxr --state spitfire_enable'],
            os='iosxr',
            platform='spitfire',
            mit=True)

        conn.connect()
        with conn.attach('0/RP0/CPU0') as console:
            out = console.execute('ls')
            self.assertIn('dummy_file', out)
        ret = conn.spawn.match.match_output
        self.assertIn('exit\r\nlogout\r\nRP/0/RP0/CPU0:Router#', ret)

    def test_attach_console_lc0(self):
        conn = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxr --state spitfire_enable'],
            os='iosxr',
            platform='spitfire',
            mit=True)

        conn.connect()
        with conn.attach('0/0/CPU0') as console:
            out = console.execute('ls')
            self.assertIn('dummy_file', out)
        ret = conn.spawn.match.match_output
        self.assertIn('exit\r\nlogout\r\nRP/0/RP0/CPU0:Router#', ret)


class TestIosXrSpitfireConfigure(unittest.TestCase):
    """Tests for config prompt handling."""

    @classmethod
    def setUpClass(cls):
        cls._conn = Connection(
            hostname='Router',
            start=[
                'mock_device_cli --os iosxr --platform spitfire --state spitfire_enable'
            ],
            os='iosxr',
            platform='spitfire')

        cls._conn.connect()

    @classmethod
    def tearDownClass(cls):
        cls._conn.disconnect()

    def test_failed_config(self):
        """Check that we can successfully return to an enable prompt after entering failed config."""
        self._conn.execute("configure terminal", allow_state_change=True)
        self._conn.execute("test failed")
        self._conn.spawn.timeout = 60
        self._conn.enable()


class TestIosXrSpitfireSyslogHandler(unittest.TestCase):
    """Tests for syslog message handling."""

    def test_connect_syslog_messages(self):
        conn = Connection(
            hostname='Router',
            start=[
                'mock_device_cli --os iosxr --platform spitfire --state spitfire_connect_syslog'
            ],
            os='iosxr',
            platform='spitfire')
        conn.connect()

    def test_connect_syslog_messages_show_tech(self):
        conn = Connection(
            hostname='Router',
            start=[
                'mock_device_cli --os iosxr --platform spitfire --state spitfire_showtech_syslog'
            ],
            os='iosxr',
            platform='spitfire',
            mit=True)

        def sendline_wrapper(func, *args, **kwargs):

            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        conn.connect()
        conn.spawn.sendline = Mock(
            side_effect=sendline_wrapper(conn.spawn.sendline))
        conn.execute('show tech')
        conn.spawn.sendline.assert_has_calls(
            [call('show tech'), call(), call()])


if __name__ == "__main__":
    unittest.main()
