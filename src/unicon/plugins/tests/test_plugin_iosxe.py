"""
Unittests for Generic/IOSXE plugin

Uses the unicon.plugins.tests.mock.mock_device_ios script to test IOSXE plugin.

"""

__author__ = "Myles Dear <mdear@cisco.com>"

import re
import unittest

from unicon import Connection
from unicon.core.errors import SubCommandFailure


class TestIosXEPluginConnect(unittest.TestCase):

    def test_asr_login_connect(self):
        c = Connection(hostname='Router',
                start=['mock_device_cli --os iosxe --state asr_login'],
                os='iosxe',
                username='cisco',
                tacacs_password='cisco')
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_isr_login_connect(self):
        c = Connection(hostname='Router',
                start=['mock_device_cli --os iosxe --state isr_login'],
                os='iosxe',
                username='cisco',
                tacacs_password='cisco',
                enable_password='cisco')
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_edison_login_connect(self):
        c = Connection(hostname='Router',
                start=['mock_device_cli --os iosxe --state cat3k_login'],
                os='iosxe',
                series='cat3k',
                username='cisco',
                tacacs_password='cisco')
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')


    def test_edison_login_connect_password_ok(self):
        c = Connection(hostname='Router',
                start=['mock_device_cli --os iosxe --state cat3k_login'],
                os='iosxe',
                series='cat3k',
                username='cisco',
                tacacs_password='cisco1')
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_cat9k_login_connect(self):
        c = Connection(hostname='Router',
                start=['mock_device_cli --os iosxe --state c9k_login4'],
                os='iosxe',
                series='cat9k',
                username='cisco',
                tacacs_password='cisco')
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_general_login_connect(self):
        c = Connection(hostname='Router',
                start=['mock_device_cli --os iosxe --state general_login'],
                os='iosxe',
                username='cisco',
                tacacs_password='cisco')
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_general_configure(self):
        c = Connection(hostname='Router',
                start=['mock_device_cli --os iosxe --state general_login'],
                os='iosxe',
                username='cisco',
                tacacs_password='cisco')
        c.connect()
        cmd = ['crypto key generate rsa general-keys modulus 2048 label ca',
               'crypto pki server ca', 'grant auto', 'hash sha256', 'lifetime ca-certificate 3650',
               'lifetime certificate 3650', 'database archive pkcs12 password 0 cisco123', 'no shutdown']
        c.configure(cmd, timeout=60, error_pattern=[], service_dialogue=None)
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_general_config_ca_profile(self):
        c = Connection(hostname='Router',
                start=['mock_device_cli --os iosxe --state general_login'],
                os='iosxe',
                username='cisco',
                tacacs_password='cisco')
        c.connect()
        c.configure("crypto pki profile enrollment test", timeout=60)
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_gkm_local_server(self):
        c = Connection(hostname='Router',
                start=['mock_device_cli --os iosxe --state general_login'],
                os='iosxe',
                username='cisco',
                tacacs_password='cisco')
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

class TestIosXEPluginExecute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
         cls.c = Connection(hostname='switch',
                            start=['mock_device_cli --os iosxe --state isr_exec'],
                            os='iosxe',
                            username='cisco',
                            tacacs_password='cisco',
                            enable_password='cisco')
         cls.c.connect()

    def test_execute_error_pattern(self):
        with self.assertRaises(SubCommandFailure) as err:
            r = self.c.execute('not a real command')

    def test_execute_error_pattern_negative(self):
        r = self.c.execute('not a real command partial')


class TestIosXEPluginDisableEnable(unittest.TestCase):

    def test_disable_enable(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxe --state isr_exec'],
                            os='iosxe',
                            username='cisco',
                            tacacs_password='cisco',
                            enable_password='cisco')

        r = c.disable()
        self.assertEqual(c.spawn.match.match_output, 'disable\r\nRouter>')

        r = c.enable()
        self.assertEqual(c.spawn.match.match_output, 'cisco\r\nRouter#')

        r = c.disable()
        self.assertEqual(c.spawn.match.match_output, 'disable\r\nRouter>')

        r = c.enable(command='enable 7')
        self.assertEqual(c.spawn.match.match_output, 'cisco\r\nRouter#')


class TestIosXEPluginPing(unittest.TestCase):

    def test_ping_success_no_vrf(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxe --state isr_exec'],
                            os='iosxe',
                            username='cisco',
                            tacacs_password='cisco',
                            enable_password='cisco')
        r = c.ping('192.0.0.5', count=30)
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
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxe --state isr_exec'],
                            os='iosxe',
                            username='cisco',
                            tacacs_password='cisco',
                            enable_password='cisco')
        r = c.ping('192.0.0.6', vrf='test', count=30)
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
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxe --state isr_exec'],
                            os='iosxe',
                            username='cisco',
                            tacacs_password='cisco',
                            enable_password='cisco')
        r = c.ping('192.0.0.6', command='ping vrf test', vrf='dont_use_this_vrf', count=30)
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

    def test_traceroute_success(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxe --state isr_exec'],
                            os='iosxe',
                            username='cisco',
                            tacacs_password='cisco',
                            enable_password='cisco')
        r = c.traceroute('192.0.0.5', count=30)
        self.maxDiff = None
        self.assertEqual(r.strip(), "\r\n".join("""traceroute
Protocol [ip]: 
Target IP address: 192.0.0.5
Ingress traceroute [n]: 
Source address or interface: 
DSCP Value [0]: 
Numeric display [n]: 
Timeout in seconds [3]: 
Probe count [3]: 
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
        c = Connection(hostname='Router',
                                start=['mock_device_cli --os iosxe --state isr_exec'],
                                os='iosxe',
                                username='cisco',
                                tacacs_password='cisco',
                                enable_password='cisco')
        r = c.traceroute('192.0.0.5', vrf='MG501', count=30)
        self.maxDiff = None
        self.assertEqual(r.strip(), "\r\n".join("""traceroute vrf MG501
Protocol [ip]: 
Target IP address: 192.0.0.5
Ingress traceroute [n]: 
Source address or interface: 
DSCP Value [0]: 
Numeric display [n]: 
Timeout in seconds [3]: 
Probe count [3]: 
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
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        with c.bash_console() as console:
            console.execute('ls')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('Router#', c.spawn.match.match_output)

    def test_bash_asr(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state asr_exec'],
                       os='iosxe',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        with c.bash_console() as console:
            console.execute('df /bootflash/')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('Router#', c.spawn.match.match_output)

class TestIosXESDWANConfigure(unittest.TestCase):
    def test_config_transaction(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state sdwan_enable'],
                       os='iosxe', series='sdwan',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        d.connect()
        d.configure('no logging console')

    def test_config_transaction_sdwan_iosxe(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state sdwan_enable'],
                       os='sdwan', series='iosxe',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco')
        d.connect()
        d.configure('no logging console')


class TestIosXECat3kPluginReload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='switch',
            start=['mock_device_cli --os iosxe --state cat3k_exec'],
            os='iosxe',
            series='cat3k',
            credentials=dict(default=dict(
                username='cisco', password='cisco'),
                alt=dict(
                username='admin', password='lab')))
        cls.c.connect()

    def test_reload(self):
        self.c.reload()


class TestIosXECat9kPluginReload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='switch',
            start=['mock_device_cli --os iosxe --state c9k_login4'],
            os='iosxe',
            series='cat9k',
            credentials=dict(default=dict(
                username='cisco', password='cisco'),
                alt=dict(
                username='admin', password='lab')))
        cls.c.connect()

    def test_reload(self):
        self.c.reload()


class TestIosXEDiol(unittest.TestCase):
    @classmethod
    def test_connection(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state standby_exec'],
                       os='iosxe',
                       init_exec_commands=[],
                       init_config_commands=[],
                       credentials=dict(default=dict(
                       username='cisco', password='cisco'),
                       alt=dict(
                       username='admin', password='lab')))

        c.connect()
    
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
                       username='admin', password='lab')))

        c.connect()

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
                       username='admin', password='lab')))

        c.connect()

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
                       username='admin', password='lab')))

        c.connect()

if __name__ == "__main__":
    unittest.main()
