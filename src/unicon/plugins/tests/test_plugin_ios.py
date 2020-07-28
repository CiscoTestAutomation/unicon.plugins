"""
Unittests for Generic/IOS plugin

Uses the unicon.plugins.tests.mock.mock_device_ios script to test IOS plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


from concurrent.futures import ThreadPoolExecutor
import os
import re
import yaml
import unittest
from unittest.mock import Mock, call, patch

import unicon
from pyats.topology import loader
from unicon import Connection
from unicon.core.errors import SubCommandFailure, ConnectionError as UniconConnectionError
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path


def mock_execute(*args, **kwargs):
    print("Mock execute: %s %s" % (args, kwargs))
    return ""

def mock_configure(*args, **kwargs):
    print("Mock configure: %s %s" % (args, kwargs))
    return ""


class TestIosPluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os ios --state login'],
                            os='ios',
                            username='cisco',
                            enable_password='cisco',
                            tacacs_password='cisco')
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_login_connect_ssh(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os ios --state connect_ssh'],
                            os='ios',
                            username='cisco',
                            enable_password='cisco',
                            tacacs_password='cisco')
        c.connect()
        self.assertEqual(c.spawn.match.match_output,'end\r\nRouter#')

    def test_connect_mit(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os ios --state login'],
                            os='ios',
                            username='cisco',
                            enable_password='cisco',
                            tacacs_password='cisco',
                            mit=True)
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'cisco\r\nRouter>')

    def test_connect_mit_check_init_commands(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os ios --state login'],
                            os='ios',
                            username='cisco',
                            enable_password='cisco',
                            tacacs_password='cisco',
                            mit=True)

        c.setup_connection = Mock()
        c.state_machine = Mock()
        c.state_machine.states = []
        c.connection_provider = c.connection_provider_class(c)
        c.spawn = Mock()
        c.spawn.buffer = ''

        c.execute = Mock(side_effect=mock_execute)
        c.configure = Mock(side_effect=mock_configure)
        c.connect()
        assert c.execute.called == False, 'Execute was called unexpectedly'
        assert c.configure.called == False, 'Configure was called unexpectedly'

    def test_login_connect_connectReply(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os ios --state login'],
                            os='ios',
                            username='cisco',
                            enable_password='cisco',
                            tacacs_password='cisco',
                            connect_reply=Dialog([[r'^(.*?)Connected.']]))
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')
        self.assertIn("^(.*?)Connected.", str(c.connection_provider.get_connection_dialog()))
        c.disconnect()

    def test_login_connect_invalid_connectReply(self):
        with self.assertRaises(SubCommandFailure) as err:
            c = Connection(hostname='Router',
                                start=['mock_device_cli --os ios --state login'],
                                os='ios',
                                username='cisco',
                                enable_password='cisco',
                                tacacs_password='cisco',
                                connect_reply='invalid_dialog')
        self.assertEqual(str(err.exception), "dialog passed via 'connect_reply' must be an instance of Dialog")

class TestIosPluginPing(unittest.TestCase):

    def test_ping_success(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os ios --state exec'],
                            os='ios',
                            username='cisco',
                            tacacs_password='cisco',
                            enable_password='cisco')
        c.ping('1.1.1.1')
        self.assertEqual("\n".join(c.spawn.match.match_output.splitlines()), """n
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 1.1.1.1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/1/1 ms
Router#""")

    def test_ping_fail(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os ios --state exec'],
                            os='ios',
                            username='cisco',
                            tacacs_password='cisco',
                            enable_password='cisco')
        try:
            c.ping('10.10.10.10')
        except SubCommandFailure:
            pass
        self.assertEqual("\n".join(c.spawn.match.match_output.splitlines()), """n
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 10.10.10.10, timeout is 2 seconds:
.....
Success rate is 0 percent (0/5)
Router#""")

    def test_ping_options(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os ios --state exec'],
                            os='ios',
                            username='cisco',
                            tacacs_password='cisco',
                            enable_password='cisco')
        r = c.ping('3.3.3.3', size=1500, count=5, ping_packet_timeout=2)
        self.assertEqual(r, "\r\n".join("""ping
Protocol [ip]: 
Target IP address: 3.3.3.3
Repeat count [5]: 5
Datagram size [100]: 1500
Timeout in seconds [2]: 2
Extended commands [n]: n
Sweep range of sizes [n]: n
Type escape sequence to abort.
Sending 5, 1500-byte ICMP Echos to 3.3.3.3, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/1/1 ms

""".splitlines()))


    def test_ping_success_vrf(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os ios --state exec'],
                            os='ios',
                            username='cisco',
                            tacacs_password='cisco',
                            enable_password='cisco')
        r = c.ping('1.1.1.1', vrf='management')
        self.assertEqual(r, "\r\n".join("""ping vrf management
Protocol [ip]: 
Target IP address: 1.1.1.1
Repeat count [5]: 
Datagram size [100]: 
Timeout in seconds [2]: 
Extended commands? [no]: n
Sweep range of sizes? [no]: n
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 1.1.1.1, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/1/3 ms

""".splitlines()))

class TestIosPluginClear(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                            start=['mock_device_cli --os ios --state exec'],
                            os='ios',
                            username='cisco',
                            tacacs_password='cisco',
                            enable_password='cisco')
        cls.c.connect()

    def test_clear_logging(self):
        c = self.c
        c.execute('clear logging')
        self.assertEqual(c.spawn.match.match_output, '\r\nRouter#')

    def test_clear_counters(self):
        c = self.c
        c.execute('clear counters')
        self.assertEqual(c.spawn.match.match_output, '\r\nRouter#')

    def test_clear_xcon_all(self):
        c = self.c
        c.execute('clear xconnect all')
        self.assertEqual(c.spawn.match.match_output, '\r\nRouter#')


class TestPasswordFailures(unittest.TestCase):

    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def test_password_failure(self):

        for pw in ['abc1', 'abc2', 'abc3']:
            c = Connection(hostname='Router',
                                start=['mock_device_cli --os ios --state login'],
                                os='ios',
                                username='cisco',
                                tacacs_password=pw)
            with self.assertRaisesRegex(UniconConnectionError, 'failed to connect to Router'):
                c.connect()

    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def test_password_failure_credential(self):

        for pw in ['abc1', 'abc2', 'abc3']:
            c = Connection(hostname='Router',
                                start=['mock_device_cli --os ios --state login'],
                                os='ios',
                                credentials=dict(default=dict(
                                    username='cisco', password=pw)))
            with self.assertRaisesRegex(UniconConnectionError, 'failed to connect to Router'):
                c.connect()


class TestIosPluginExecute(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                            start=['mock_device_cli --os ios --state exec'],
                            os='ios',
                            username='cisco',
                            tacacs_password='cisco',
                            enable_password='cisco',
                            init_exec_commands=[],
                            init_config_commands=[])
        cls.c.connect()
        with open(os.path.join(mockdata_path, 'ios/ios_mock_data.yaml'), 'rb') as datafile:
            cls.command_data = yaml.safe_load(datafile.read())

    def test_iterate_list_of_commands(self):
        command_data_list = self.command_data['exec']['commands']['show int e0/0']['response']
        for expected_output in command_data_list:
            output = self.c.execute('show int e0/0').replace('\r', '')
            self.assertEqual(output, expected_output.rstrip())

    def test_execute_with_yes_no_prompt(self):
        self.c.execute('clear something', timeout=15)
        self.assertEqual(self.c.spawn.match.match_output, 'y\r\nRouter#')

    def test_execute_error_pattern(self):
        with self.assertRaises(SubCommandFailure) as err:
            r = self.c.execute('not a real command')


    def test_execute_error_pattern_negative(self):
        r = self.c.execute('not a real command partial')


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestIosPluginReload(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c1 = Connection(hostname='Router1',
                            start=['mock_device_cli --os ios --state enable'],
                            os='ios',
                            username='cisco',
                            tacacs_password='cisco',
                            enable_password='cisco')
        cls.c2 = Connection(hostname='Router2',
                            start=['mock_device_cli --os ios --state enable'],
                            os='ios',
                            username='cisco',
                            tacacs_password='cisco',
                            enable_password='cisco')
        cls.c3 = Connection(hostname='Router3',
                            start=['mock_device_cli --os ios --state enable'],
                            os='ios',
                            username='cisco',
                            tacacs_password='cisco',
                            enable_password='cisco')
        cls.c1.connect()
        cls.c2.connect()
        cls.c3.connect()

    @classmethod
    def tearDownClass(cls):
        cls.c1.disconnect()
        cls.c2.disconnect()
        cls.c3.disconnect()

    def test_reload_with_multi_thread(self):
        with ThreadPoolExecutor(max_workers=3) as executor:
            tasks = [executor.submit(dev.reload, timeout=20)
                     for dev in [self.c1, self.c2, self.c3]]
            results = [task.result() for task in tasks]


class TestIosPagentPluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os ios --state pagent_disable_without_license'],
                            os='ios',
                            series='pagent',
                            username='cisco',
                            enable_password='cisco',
                            tacacs_password='cisco',
                            pagent_key='899573834241')
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestIosPluginConnectCredentials(unittest.TestCase):

    def setUp(self):
        self.testbed = """
        devices:
          Router:
            os: ios
            type: router
            credentials:
                default:
                    username: admin
                    password: cisco
                    enable_password: enpasswd
            connections:
              defaults:
                class: unicon.Unicon
              a:
                command: "mock_device_cli --os ios --state login_enable"
        """

    def test_connect(self):
        tb = loader.load(self.testbed)
        r = tb.devices.Router
        r.connect()
        self.assertEqual(r.is_connected(), True)


if __name__ == "__main__":
    unittest.main()

