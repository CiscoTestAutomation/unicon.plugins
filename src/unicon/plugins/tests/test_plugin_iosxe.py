"""
Unittests for Generic/IOSXE plugin

Uses the unicon.plugins.tests.mock.mock_device_ios script to test IOSXE plugin.

"""

__author__ = "Myles Dear <mdear@cisco.com>"

import re
import unittest
from unittest.mock import patch

from pyats.topology import loader

import unicon
from unicon import Connection
from unicon.eal.dialogs import Dialog, Statement
from unicon.core.errors import SubCommandFailure, StateMachineError, UniconAuthenticationError, ConnectionError as UniconConnectionError
from unicon.plugins.tests.mock.mock_device_iosxe import MockDeviceTcpWrapperIOSXE

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXEPluginConnect(unittest.TestCase):

    def test_asr_login_connect(self):
        c = Connection(hostname='Router',
                start=['mock_device_cli --os iosxe --state asr_login --hostname Router'],
                os='iosxe',
                credentials=dict(default=dict(username='cisco', password='cisco')),
                log_buffer=True)
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_isr_login_connect(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state isr_login --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_edison_login_connect(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state cat3k_login --hostname Router'],
                       os='iosxe',
                       platform='cat3k',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_edison_login_connect_password_ok(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state cat3k_login --hostname Router'],
                       os='iosxe',
                       platform='cat3k',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_general_login_connect(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_login --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_general_login_connect_syslog(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state connect_syslog --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_general_configure(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_login --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        c.connect()
        cmd = ['crypto key generate rsa general-keys modulus 2048 label ca',
               'crypto pki server ca', 'grant auto', 'hash sha256', 'lifetime ca-certificate 3650',
               'lifetime certificate 3650', 'database archive pkcs12 password 0 cisco123', 'no shutdown']
        c.configure(cmd, timeout=60, error_pattern=[], service_dialogue=None)
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_general_config_ca_profile(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_login --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        c.connect()
        c.configure("crypto pki profile enrollment test", timeout=60)
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_gkm_local_server(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_login --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        c.connect()
        cmd = [
            "crypto gkm group g1",
            "identity number 101",
            "server local",
            "end",
            "end"
        ]
        c.configure(cmd, timeout=60)
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_login_console_server_sendline_after(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='ts_login')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            settings=dict(SENDLINE_AFTER_CRED='ts'),
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             ts=dict(username='ts_user', password='ts_pw')),
            login_creds=['ts', 'default'],
            connection_timeout=10
        )
        try:
            c.connect()
        finally:
            c.disconnect()
            md.stop()

    def test_login_console_server_post_cred_action(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='ts_login')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             ts=dict(username='ts_user', password='ts_pw')),
            login_creds=['ts', 'default'],
            cred_action=dict(ts=dict(post='sendline()')),
            connection_timeout=10
        )
        try:
            c.connect()
        finally:
            c.disconnect()
            md.stop()


class TestIosXEPluginExecute(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='switch',
                           start=['mock_device_cli --os iosxe --state isr_exec'],
                           os='iosxe',
                           credentials=dict(default=dict(username='cisco', password='cisco')),
                           log_buffer=True
                           )
        cls.c.connect()

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()

    def test_execute_error_pattern(self):
      for cmd in ['not a real command', 'badcommand']:
        with self.assertRaises(SubCommandFailure) as err:
            r = self.c.execute(cmd)

    def test_execute_error_pattern_negative(self):
        r = self.c.execute('not a real command partial')

    def test_execute_stmt_list(self):
      for cmd in ['install remove inactive']:
        r = self.c.execute(cmd)

    def test_execute_with_msgs(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='enable_with_msgs')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            credentials=dict(default=dict(username='cisco', password='cisco')),
            mit=True
        )
        try:
            c.connect()
            c.execute('msg')
        finally:
            c.disconnect()
            md.stop()


class TestIosXEPluginDisableEnable(unittest.TestCase):

    def test_disable_enable(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state isr_exec'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )

        r = c.disable()
        self.assertEqual(c.spawn.match.match_output, 'disable\r\nRouter>')

        r = c.enable()
        self.assertEqual(c.spawn.match.match_output, 'cisco\r\nRouter#')

        r = c.disable()
        self.assertEqual(c.spawn.match.match_output, 'disable\r\nRouter>')

        r = c.enable(command='enable 7')
        self.assertEqual(c.spawn.match.match_output, 'cisco\r\nRouter#')

        c.disconnect()

    def test_disable_to_enable_with_msg(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state disable_to_enable_with_msg'],
                       os='iosxe',
                       credentials=dict(default=dict(password='cisco')),
                       log_buffer=True
                       )
        c.connect()
        c.disconnect()


class TestIosXEPluginPing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                           start=['mock_device_cli --os iosxe --state isr_exec'],
                           os='iosxe',
                           credentials=dict(default=dict(username='cisco', password='cisco')),
                           log_buffer=True
                           )
        cls.c.connect()

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()

    def test_ping_success_no_vrf(self):
        r = self.c.ping('192.0.0.5', count=30)
        self.maxDiff = None
        self.assertEqual(r.strip(), "\r\n".join("""ping
Protocol [ip]: 
Target IP address: 192.0.0.5
Repeat count [5]: 30
Datagram size [100]: 
Timeout in seconds [2]: 
Extended commands [n]: n
Sweep range of sizes [n]: n
Type escape sequence to abort.
Sending 30, 100-byte ICMP Echos to 192.0.0.5, timeout is 2 seconds:
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Success rate is 100 percent (30/30), round-trip min/avg/max = 1/1/3 ms""".\
splitlines()))

    def test_ping_success_vrf(self):
        r = self.c.ping('192.0.0.6', vrf='test', count=30)
        self.assertEqual(r.strip(), "\r\n".join("""ping vrf test
Protocol [ip]: 
Target IP address: 192.0.0.6
Repeat count [5]: 30
Datagram size [100]: 
Timeout in seconds [2]: 
Extended commands [n]: n
Sweep range of sizes [n]: n
Type escape sequence to abort.
Sending 30, 100-byte ICMP Echos to 192.0.0.6, timeout is 2 seconds:
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Success rate is 100 percent (30/30), round-trip min/avg/max = 1/1/3 ms""".\
splitlines()))

    def test_ping_success_vrf_in_cmd(self):
        r = self.c.ping('192.0.0.6', command='ping vrf test', vrf='dont_use_this_vrf', count=30)
        self.assertEqual(r.strip(), "\r\n".join("""ping vrf test
Protocol [ip]: 
Target IP address: 192.0.0.6
Repeat count [5]: 30
Datagram size [100]: 
Timeout in seconds [2]: 
Extended commands [n]: n
Sweep range of sizes [n]: n
Type escape sequence to abort.
Sending 30, 100-byte ICMP Echos to 192.0.0.6, timeout is 2 seconds:
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Success rate is 100 percent (30/30), round-trip min/avg/max = 1/1/3 ms""".\
splitlines()))


class TestIosxePlugingTraceroute(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                           start=['mock_device_cli --os iosxe --state isr_exec'],
                           os='iosxe',
                           credentials=dict(default=dict(username='cisco', password='cisco')),
                           log_buffer=True
                           )
        cls.c.connect()

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()

    def test_traceroute_success(self):
        r = self.c.traceroute('192.0.0.5', probe=30)
        self.maxDiff = None
        self.assertEqual(r.strip(), "\r\n".join("""traceroute
Protocol [ip]: 
Target IP address: 192.0.0.5
Ingress traceroute [n]: 
Source address or interface: 
DSCP Value [0]: 
Numeric display [n]: 
Timeout in seconds [3]: 
Probe count [3]: 30
Minimum Time to Live [1]: 
Maximum Time to Live [30]: 
Port Number [33434]: 
Loose, Strict, Record, Timestamp, Verbose[none]: 
Type escape sequence to abort.
Tracing the route to 192.0.0.5
VRF info: (vrf in name/id, vrf out name/id)
  1 192.0.0.5 msec *  1 msec""".\
splitlines()))

    def test_traceroute_vrf(self):
        r = self.c.traceroute('192.0.0.5', vrf='MG501', probe=30)
        self.maxDiff = None
        self.assertEqual(r.strip(), "\r\n".join("""traceroute vrf MG501
Protocol [ip]: 
Target IP address: 192.0.0.5
Ingress traceroute [n]: 
Source address or interface: 
DSCP Value [0]: 
Numeric display [n]: 
Timeout in seconds [3]: 
Probe count [3]: 30
Minimum Time to Live [1]: 
Maximum Time to Live [30]: 
Port Number [33434]: 
Loose, Strict, Record, Timestamp, Verbose[none]: 
Type escape sequence to abort.
Tracing the route to 192.0.0.5
VRF info: (vrf in name/id, vrf out name/id)
  1 192.0.0.5 msec *  1 msec""".\
splitlines()))


class TestIosXEluginBashService(unittest.TestCase):

    def test_bash(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state isr_exec'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )
        with c.bash_console() as console:
            console.execute('ls')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('Router#', c.spawn.match.match_output)
        c.disconnect()

    def test_bash_asr(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state asr_exec'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )
        with c.bash_console() as console:
            console.execute('df /bootflash/')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('Router#', c.spawn.match.match_output)
        c.disconnect()

class TestIosXESDWANConfigure(unittest.TestCase):

    def test_config_transaction(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state sdwan_enable'],
                       os='iosxe', platform='sdwan',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )

        d.connect()
        d.configure('no logging console')
        d.disconnect()

    def test_config_transaction_sdwan_iosxe(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state sdwan_enable'],
                       os='sdwan', platform='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )

        d.connect()
        d.configure('no logging console')
        d.disconnect()

    def test_config_transaction_sdwan_iosxe_confirm(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state sdwan_enable2'],
                       os='iosxe', platform='sdwan',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True,
                       mit=True
                       )

        d.connect()
        d.configure('no logging console')
        d.disconnect()


class TestIosXEC8KvPluginReload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='switch',
            start=['mock_device_cli --os iosxe --state c8kv_exec'],
            os='iosxe',
            platform='c8kv',
            credentials=dict(default=dict(
                username='cisco', password='cisco'),
                alt=dict(
                username='admin', password='lab')),
            log_buffer=True
            )
        cls.c.connect()

    @classmethod
    def tearDownClass(cls):
         cls.c.disconnect()

    def test_reload(self):
        self.c.reload(grub_boot_image='GOLDEN')


class TestIosXECat3kPluginReload(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='switch',
            start=['mock_device_cli --os iosxe --state cat3k_exec'],
            os='iosxe',
            platform='cat3k',
            credentials=dict(default=dict(
                username='cisco', password='cisco'),
                alt=dict(
                username='admin', password='lab')),
            log_buffer=True
            )

        cls.c.connect()

    @classmethod
    def tearDownClass(cls):
         cls.c.disconnect()
    def test_reload(self):
        self.c.reload()


class TestIosXEDiol(unittest.TestCase):

    def test_connection(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state standby_exec'],
                       os='iosxe',
                       init_exec_commands=[],
                       init_config_commands=[],
                       credentials=dict(default=dict(
                       username='cisco', password='cisco'),
                       alt=dict(
                       username='admin', password='lab')),
                       log_buffer=True
                       )

        c.connect()
        c.disconnect()

    def test_connection_diol_exec(self):
        c = Connection(hostname='RouterRP',
                       start=['mock_device_cli --os iosxe --state diol_exec'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       credentials=dict(default=dict(
                       username='cisco', password='cisco'),
                       alt=dict(
                       username='admin', password='lab')),
                       log_buffer=True
                       )

        c.connect()
        c.disconnect()

    def test_connection_diol_enable(self):
        c = Connection(hostname='RouterRP',
                       start=['mock_device_cli --os iosxe --state diol_enable'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       credentials=dict(default=dict(
                       username='cisco', password='cisco'),
                       alt=dict(
                       username='admin', password='lab')),
                       log_buffer=True
                       )

        c.connect()
        c.disconnect()

    def test_connection_diol_disable(self):
        c = Connection(hostname='RouterRP',
                       start=['mock_device_cli --os iosxe --state diol_disable'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       credentials=dict(default=dict(
                       username='cisco', password='cisco'),
                       alt=dict(
                       username='admin', password='lab')),
                       log_buffer=True
                       )

        c.connect()
        c.disconnect()


class TestIosXEConfigure(unittest.TestCase):

    def test_configure_are_you_sure_ywtdt(self):
        c = Connection(hostname='RouterRP',
                       start=['mock_device_cli --os iosxe --state general_enable'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True
                       )
        c.connect()
        c.configure(['crypto pki trustpoint test', 'no crypto pki trustpoint test'])
        c.disconnect()

    def test_configure_error_pattern(self):
        c = Connection(hostname='RouterRP',
                       start=['mock_device_cli --os iosxe --state general_enable'],
                       os='iosxe',
                       init_exec_commands=[],
                       log_buffer=True
                       )
        c.connect()
        for cmd in ['ntp server vrf foo 1.2.3.4']:
          with self.assertRaises(SubCommandFailure) as err:
              r = c.configure(cmd)
        c.disconnect()
    def test_configure_with_msgs(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='config_with_msgs')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            credentials=dict(default=dict(username='cisco', password='cisco')),
            mit=True,
        )
        try:
            c.connect()
            c.configure('msg')
        finally:
            c.disconnect()
            md.stop()

    def test_configure_with_msgs2(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='config_with_msgs2')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            credentials=dict(default=dict(username='cisco', password='cisco')),
            mit=True
        )
        try:
            c.connect()
            c.configure('msg')
        finally:
            c.disconnect()
            md.stop()

    def test_config_locked(self):
        c = Connection(hostname='RouterRP',
                       start=['mock_device_cli --os iosxe --state general_enable'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True
                       )
        c.connect()

        c.execute('set config lock count 2')
        c.settings.CONFIG_LOCK_RETRIES = 0
        c.settings.CONFIG_LOCK_RETRY_SLEEP = 0

        with self.assertRaises(StateMachineError):
            c.configure('')

        c.execute('set config lock count 2')
        with self.assertRaises(StateMachineError):
            c.configure('', lock_retries=1, lock_retry_sleep=1)

        c.execute('set config lock count 3')
        c.settings.CONFIG_LOCK_RETRIES = 1
        c.settings.CONFIG_LOCK_RETRY_SLEEP = 1
        with self.assertRaises(StateMachineError):
            c.configure('')

        c.execute('set config lock count 3')
        c.settings.CONFIG_LOCK_RETRIES = 5
        c.settings.CONFIG_LOCK_RETRY_SLEEP = 1
        c.configure('')

        c.disconnect()

    def test_slow_config_mode(self):
        c = Connection(hostname='Switch',
                       start=['mock_device_cli --os iosxe --state slow_config_mode'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True
                       )
        c.connect()
        c.configure(['no logging console'])
        c.disconnect()

    def test_slow_config_lock(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='config_locked')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            mit=True,
            log_buffer=True,
        )
        try:
            c.connect()
            c.settings.CONFIG_TIMEOUT=5
            c.settings.CONFIG_LOCK_RETRY_SLEEP=3
            c.configure(['no logging console'])
        finally:
            c.disconnect()
            md.stop()

    def test_config_no_service_prompt_config(self):
        c = Connection(hostname='Switch',
                       start=['mock_device_cli --os iosxe --state enable_no_service_prompt_config'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True
                       )
        c.connect()
        c.configure(['no logging console'])
        c.disconnect()


class TestIosXEEnableSecret(unittest.TestCase):

    def test_enable_secret(self):
        c = Connection(hostname='R1',
                       start=['mock_device_cli --os iosxe --state initial_config_dialog --hostname R1'],
                       os='iosxe',
                       init_exec_commands=[],
                       init_config_commands=[],
                       credentials=dict(default=dict(password='Secret12345')),
                       log_buffer=True
                       )
        c.connect()
        c.configure(['no logging console'])
        c.disconnect()

    def test_bad_enable_secret(self):
        c = Connection(hostname='R1',
                       start=['mock_device_cli --os iosxe --state initial_config_dialog --hostname R1'],
                       os='iosxe',
                       init_exec_commands=[],
                       init_config_commands=[],
                       credentials=dict(default=dict(password='badpw')),
                       log_buffer=True
                       )
        with self.assertRaisesRegex(UniconConnectionError, 'failed to connect to R1'):
            c.connect()
        c.disconnect()

    def test_enable_secret_topology_legacy(self):
        tb = loader.load("""
        devices:
          R1:
            os: iosxe
            passwords:
                enable: Secret12345
            connections:
              cli:
                command: mock_device_cli --os iosxe --state initial_config_dialog --hostname R1
                arguments:
                  log_buffer: True
                  init_exec_commands: []
                  init_config_commands: []
        """)
        dev = tb.devices.R1
        dev.connect()
        dev.disconnect()

    def test_enable_secret_topology(self):
        tb = loader.load("""
        devices:
          R1:
            os: iosxe
            credentials:
              default:
                password: Secret12345
            connections:
              cli:
                command: mock_device_cli --os iosxe --state initial_config_dialog --hostname R1
                arguments:
                  log_buffer: True
                  init_exec_commands: []
                  init_config_commands: []
        """)
        dev = tb.devices.R1
        dev.connect()
        dev.disconnect()


class TestIosXEluginGuestShellService(unittest.TestCase):

    def test_guestshell(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_enable --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )
        with c.guestshell() as console:
            output = console.execute('pwd')
            self.assertEqual(output, '/home/guestshell')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('Router#', c.spawn.match.match_output)
        c.disconnect()

    def test_guestshell_activate(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_enable --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )
        with c.guestshell(enable_guestshell=True) as console:
            output = console.execute('pwd')
            self.assertEqual(output, '/home/guestshell')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('Router#', c.spawn.match.match_output)
        c.disconnect()

    def test_guestshell_activate_configure(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state enable_guestshell --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True,
                       mit=True
                       )
        with c.guestshell(enable_guestshell=True) as console:
            output = console.execute('pwd')
            self.assertEqual(output, '/home/guestshell')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('Router#', c.spawn.match.match_output)
        c.disconnect()

class TestIosXEping(unittest.TestCase):

    def test_ping_failed_protocol(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='ping_fail', hostname='PE1')
        md.start()

        c = Connection(
            hostname='PE1',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            connection_timeout=10,
            mit=True
        )
        try:
            c.connect()
            try:
                c.ping('10.10.10.10')
            except Exception:
                pass
            c.configure()
        except Exception:
            raise
        finally:
            c.disconnect()
            md.stop()


class TestSyslogHandler(unittest.TestCase):

    def test_syslog_handler_timeout(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state endless_syslog --hostname PE1'],
            os='iosxe',
            connection_timeout=5,
            settings=dict(PROMPT_RECOVERY_COMMANDS = ['\x06']),
            prompt_recovery=True
        )
        try:
            c.connect()
        except Exception:
            raise
        finally:
            c.disconnect()


class TestIosxeAsr1k(unittest.TestCase):
    def test_connect_asr1k_ha(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='ha_asr1k_exec,ha_asr1k_stby_exec', hostname='R1')
        md.start()

        c = Connection(
            hostname='R1',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1])
            ],
            os='iosxe',
            connection_timeout=10,
            mit=True
        )
        try:
            c.connect()
        except Exception:
            raise
        finally:
            c.disconnect()
            md.stop()

    def test_connect_asr1k_ha_rommon(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='ha_asr1k_exec,ha_asr1k_stby_exec', hostname='R1')
        md.start()

        c = Connection(
            hostname='R1',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1])
            ],
            os='iosxe',
            connection_timeout=10,
            credentials=dict(default=dict(password='lab'))
        )
        try:
            c.connect()
            c.execute('reload_to_rommon')
            c.rommon()
            c.enable(target='active')
            c.enable(target='standby')
        except Exception:
            raise
        finally:
            c.disconnect()
            md.stop()

    def test_connect_asr1k_ha_rommon_boot_image(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='ha_asr1k_exec,ha_asr1k_stby_exec', hostname='R1')
        md.start()

        c = Connection(
            hostname='R1',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1])
            ],
            os='iosxe',
            connection_timeout=10,
            credentials=dict(default=dict(password='lab'))
        )
        try:
            c.connect()
            c.execute('reload_to_rommon')
            c.rommon()
            c.enable(target='active', image='test/packages.conf')
            c.enable(target='standby', image='test/packages.conf')

            c.execute('reload_to_rommon')
            c.rommon()
            c.enable(target='active', image_to_boot='test/packages.conf')
            c.enable(target='standby', image_to_boot='test/packages.conf')
        except Exception:
            raise
        finally:
            c.disconnect()
            md.stop()


class TestIosxeTclsh(unittest.TestCase):

    def test_tclsh(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()
        c.tclsh()
        c.enable()
        c.disconnect()


if __name__ == "__main__":
    unittest.main()
