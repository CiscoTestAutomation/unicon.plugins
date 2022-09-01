"""
Unittests for Generic/aos plugin

Uses the unicon.plugins.tests.mock.mock_device_aos script to test aos plugin.

"""

__author__ = "Alex Pfeil apfeil@amfam.com"


from concurrent.futures import ThreadPoolExecutor
import os
import re
import yaml
import unittest
from unittest.mock import Mock, call, patch

import unicon
from pyats.topology import loader
from unicon import Connection
from unicon.core.errors import EOF, SubCommandFailure, ConnectionError as UniconConnectionError
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path


def mock_execute(*args, **kwargs):
    print("Mock execute: %s %s" % (args, kwargs))
    return ""

def mock_configure(*args, **kwargs):
    print("Mock configure: %s %s" % (args, kwargs))
    return ""


class TestaosPluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os aos --state login'],
                            os='aos',
                            init_exec_commands=[],
                            init_config_commands=[],
                            credentials=dict(default=dict(username='aruba', password='aruba')))
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'enable\r\nRouter#')

    def test_login_connect_ssh(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os aos --state connect_ssh'],
                            os='aos',
                            init_exec_commands=[],
                            init_config_commands=[],
                            credentials=dict(default=dict(username='aruba', password='aruba')))
        c.connect()
        self.assertEqual(c.spawn.match.match_output,'enable\r\nRouter#')

    def test_connect_mit(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os aos --state login'],
                            os='aos',
                            init_exec_commands=[],
                            init_config_commands=[],
                            credentials=dict(default=dict(username='aruba', password='aruba')),
                            mit=True)
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'exit\r\nRouter>')

    def test_connect_mit_check_init_commands(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os aos --state login'],
                            os='aos',
                            init_exec_commands=[],
                            init_config_commands=[],
                            credentials=dict(default=dict(username='aruba', password='aruba')),
                            mit=True)

        c.setup_connection = Mock()
        c.state_machine = Mock()
        c.state_machine.states = []
        c._get_learned_hostname = Mock(return_value='Router')
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
                            start=['mock_device_cli --os aos --state login'],
                            os='aos',
                            init_exec_commands=[],
                            init_config_commands=[],
                            credentials=dict(default=dict(username='aruba', password='aruba')),
                            connect_reply=Dialog([[r'^(.*?)Connected.']]))
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'enable\r\nRouter#')
        self.assertIn("^(.*?)Connected.", str(c.connection_provider.get_connection_dialog()))
        c.disconnect()

    def test_login_connect_invalid_connectReply(self):
        with self.assertRaises(SubCommandFailure) as err:
            c = Connection(hostname='Router',
                                start=['mock_device_cli --os aos --state login'],
                                os='aos',
                                init_exec_commands=[],
                                init_config_commands=[],
                                credentials=dict(default=dict(username='aruba', password='aruba')),
                                connect_reply='invalid_dialog')
        self.assertEqual(str(err.exception), "dialog passed via 'connect_reply' must be an instance of Dialog")

class TestaosPluginPing(unittest.TestCase):

    def test_ping_success(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os aos --state login'],
                            os='aos',
                            init_exec_commands=[],
                            init_config_commands=[],
                            credentials=dict(default=dict(username='aruba', password='aruba')))
        c.ping('1.1.1.1')
        self.assertEqual("\n".join(c.spawn.match.match_output.splitlines()), """ping 1.1.1.1
1.1.1.1 is alive, time = 9 ms
Router#""")

    def test_ping_fail(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os aos --state login'],
                            os='aos',
                            init_exec_commands=[],
                            init_config_commands=[],
                            credentials=dict(default=dict(username='aruba', password='aruba')))
        try:
            c.ping('10.10.10.10')
        except SubCommandFailure:
            pass
        self.assertEqual("\n".join(c.spawn.match.match_output.splitlines()), """ping 10.10.10.10
Request timed out.
Router#""")

class TestPasswordFailures(unittest.TestCase):

    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def test_password_failure(self):

        for pw in ['abc1', 'abc2', 'abc3']:
            c = Connection(hostname='Router',
                                start=['mock_device_cli --os aos --state login'],
                                os='aos',
                                credentials=dict(default=dict(username='aruba', password=pw)))
            with self.assertRaisesRegex(UniconConnectionError, 'failed to connect to Router'):
                c.connect()

    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def test_password_failure_credential(self):

        for pw in ['abc1', 'abc2', 'abc3']:
            c = Connection(hostname='Router',
                                start=['mock_device_cli --os aos --state login'],
                                os='aos',
                                credentials=dict(default=dict(username='aruba', password=pw)))
            with self.assertRaisesRegex(UniconConnectionError, 'failed to connect to Router'):
                c.connect()


class TestaosPluginExecute(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                           start=['mock_device_cli --os aos --state login'],
                           os='aos',
                           credentials=dict(default=dict(username='aruba', password='aruba')),
                           init_exec_commands=[],
                           init_config_commands=[])
        cls.c.connect()
        with open(os.path.join(mockdata_path, 'aos/aos_mock_data.yaml'), 'rb') as datafile:
            cls.command_data = yaml.safe_load(datafile.read())
    maxDiff = None
    def test_iterate_list_of_commands(self):
        command_data_list = self.command_data['exec']['commands']['show int 1/1']['response']
        output = self.c.execute('show int 1/1')
        expected_output = '''Status and Counters - Port Counters for port 1/1
Name  : data
MAC Address      : 123456-7890ab
Link Status      : Down
Port Enabled     : Yes
Totals (Since boot or last clear) :
Bytes Rx        : 0                    Bytes Tx        : 0
Unicast Rx      : 0                    Unicast Tx      : 0
Bcast/Mcast Rx  : 0                    Bcast/Mcast Tx  : 0
Errors (Since boot or last clear) :
FCS Rx          : 0                    Drops Tx        : 0
Alignment Rx    : 0                    Collisions Tx   : 0
Runts Rx        : 0                    Late Colln Tx   : 0
Giants Rx       : 0                    Excessive Colln : 0
Total Rx Errors : 0                    Deferred Tx     : 0
Others (Since boot or last clear) :
Discard Rx      : 0                    Out Queue Len   : 0
Unknown Protos  : 0
Rates (5 minute weighted average) :
Total Rx (bps) : 0                     Total Tx (bps) : 0
Unicast Rx (Pkts/sec) : 0              Unicast Tx (Pkts/sec) : 0
B/Mcast Rx (Pkts/sec) : 0              B/Mcast Tx (Pkts/sec) : 0
Utilization Rx  :     0 %              Utilization Tx  :     0 %
        self.assertEqual(output, expected_output)'''


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)

class TestaosPluginConnectCredentials(unittest.TestCase):

    def setUp(self):
        self.testbed = """
        devices:
          Router:
            os: aos
            type: router
            credentials:
                default:
                    username: aruba
                    password: aruba
                    enable_password: enpasswd
            connections:
              defaults:
                class: unicon.Unicon
              a:
                command: "mock_device_cli --os aos --state login"
        """

    def test_connect(self):
        tb = loader.load(self.testbed)
        r = tb.devices.Router
        r.connect()
        self.assertEqual(r.is_connected(), True)


class TestaosPluginConfigure(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                           start=['mock_device_cli --os aos --state login'],
                           os='aos',
                           credentials=dict(default=dict(username='aruba',password='aruba')),
                           init_exec_commands=[],
                           init_config_commands=[],
                           settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2))
        cls.c.connect()

    def test_configure_exception(self):
        try:
            self.c.configure('invalid command')
        except:
            pass
    
    def test_configure_hostname(self):
        try:
            self.c.configure('hostname R1')
        except:
            pass

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()


if __name__ == "__main__":
    unittest.main()
