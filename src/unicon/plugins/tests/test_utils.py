import os
import unittest
from pathlib import Path
from pyats.topology.loader import load
from unittest.mock import MagicMock, patch
from unicon.plugins.utils import AbstractTokenDiscovery
from unicon.plugins.utils import load_token_csv_file
from unicon.plugins.tests.mock.mock_device_generic import (
    MockDeviceTcpWrapperGeneric
)


class TestAbstractTokenDiscoveryConnection(unittest.TestCase):
    """ Run unit testing on AbstractTokenDiscovery
        Test that connections work, tokens get discovered, and connections get
        redirected to corresponding plugins
    """

    def setUp(self) -> None:
        self.mock_con = MagicMock()
        self.testbed = """
devices:
    R1:
        credentials:
            default:
                username: cisco
                password: cisco
        connections:
            defaults:
                class: unicon.Unicon
            cli:
                command: ""
                settings:
                    POST_DISCONNECT_WAIT_SEC: 0
                    GRACEFUL_DISCONNECT_WAIT_SEC: 0.2
                    INIT_EXEC_COMMANDS: []
                    INIT_CONFIG_COMMANDS: []
                    SLEEP_PRE_LAUNCH: 0.2
        """
        self.tb = load(self.testbed)
        self.dev = self.tb.devices.R1


    def test_asa_learn_tokens_from_show_version(self):
        # Set up device to use correct mock_device data
        self.dev.connections.cli.command = \
            "mock_device_cli --os generic --state asa_username --hostname ASA"
        self.dev.platform = "iamu571_overwriteme"
        self.dev.connections.cli['arguments'] = {}
        self.dev.connections.cli['arguments']['learn_tokens'] = True
        self.dev.connections.cli['arguments']['learn_hostname'] = True
        self.dev.connections.cli['arguments']['overwrite_testbed_tokens'] = True

        # Test connection succeeds and tokens learned
        self.dev.connect()
        self.assertEqual(self.dev.os, 'asa')
        self.assertEqual(self.dev.version, '8.4.1')
        self.assertEqual(self.dev.platform, 'asa5520')

        # Test that connection was redirected to the corresponding plugin
        with open(self.dev.logfile) as f:
            log_contents = f.read()
        self.assertRegex(
            log_contents,
            r'\+\+\+ Unicon plugin asa( \(unicon\.plugins\.asa\))? \+\+\+'
        )


    def test_ios_learn_tokens_from_show_version(self):
        # Set up device to use correct mock_device data
        self.dev.connections.cli.command = \
            "mock_device_cli --os generic --state ios_login"

        # Test connection succeeds and tokens learned
        self.dev.connect(learn_tokens=True, learn_hostname=True)
        self.assertEqual(self.dev.state_machine.current_state, 'enable')
        self.assertEqual(self.dev.os, 'ios')
        self.assertEqual(self.dev.version, '15')
        self.assertEqual(self.dev.platform, 'c7200p')
        self.assertEqual(self.dev.pid, '7206VXR')

        # Test that connection was redirected to the corresponding plugin
        with open(self.dev.logfile) as f:
            log_contents = f.read()
        self.assertRegex(
            log_contents,
            r'\+\+\+ Unicon plugin ios( \(unicon\.plugins\.ios\))? \+\+\+'
        )

    # Test that finding a pid from show version that exists in refernce file,
    # is enough to get all tokens. 'show inventory' not called
    def test_iosxe_learn_tokens_from_show_version_pid_number(self):
        # Set up device to use correct mock_device data
        self.dev.connections.cli.command = \
            "mock_device_cli --os generic --state iosxe_login"

        # Test connection succeeds and tokens learned
        self.dev.connect(learn_tokens=True, learn_hostname=True)
        self.assertEqual(self.dev.os, 'iosxe')
        self.assertEqual(self.dev.version, '15.2')
        self.assertEqual(self.dev.platform, 'asr1k')
        self.assertEqual(self.dev.model, 'asr1000')
        self.assertEqual(self.dev.pid, 'ASR1006')

        # Test that connection was redirected to the corresponding plugin
        with open(self.dev.logfile) as f:
            log_contents = f.read()
        self.assertRegex(
            log_contents,
            r'\+\+\+ Unicon plugin iosxe( \(unicon\.(internal\.)?plugins\.iosxe\))? \+\+\+'
        )
    # test for controller mode for sdwan
    def test_iosxe_learn_tokens_from_show_version_sdwan(self):
        # Set up device to use correct mock_device data
        self.dev.connections.cli.command = \
            "mock_device_cli --os generic --state iosxe_login3"

        # Test connection succeeds and tokens learned
        self.dev.connect(learn_tokens=True)
        self.assertEqual(self.dev.os, 'iosxe')
        self.assertEqual(self.dev.version, '17.14')
        self.assertEqual(self.dev.platform, 'sdwan')
        self.assertEqual(self.dev.model, 'c5000')
        self.assertEqual(self.dev.pid, 'WS-C5002')

    def test_iosxr_learn_tokens_from_show_version(self):
        # Set up device to use correct mock_device data
        self.dev.connections.cli.command = \
            "mock_device_cli --os generic --state iosxr_login"

        # Test connection succeeds and tokens learned
        self.dev.connect(learn_tokens=True, learn_hostname=True)
        self.assertEqual(self.dev.os, 'iosxr')
        self.assertEqual(self.dev.os_flavor, 'lnt')
        self.assertEqual(self.dev.version, '5.2.3.12i')
        self.assertEqual(self.dev.platform, 'iosxrv')

        # Test that connection was redirected to the corresponding plugin
        with open(self.dev.logfile) as f:
            log_contents = f.read()
        self.assertRegex(
            log_contents,
            r'\+\+\+ Unicon plugin iosxr/iosxrv( \(unicon\.plugins\.iosxr\.iosxrv\))? \+\+\+'
        )

    def test_nxos_learn_tokens_from_show_version(self):
        # Set up device to use correct mock_device data
        self.dev.connections.cli.command = \
            "mock_device_cli --os generic --state nxos_login"
        self.dev.connections.cli.settings['LEARN_DEVICE_TOKENS'] = True

        # Test connection succeeds and tokens learned
        self.dev.connect(learn_hostname=True)
        self.assertEqual(self.dev.os, 'nxos')
        self.assertEqual(self.dev.version, '7.3.5n1.1')
        self.assertEqual(self.dev.platform, 'n5k')
        self.assertEqual(self.dev.model, 'n5500')
        self.assertEqual(self.dev.pid, 'N5K-C5548P')

        # Test that connection was redirected to the corresponding plugin
        with open(self.dev.logfile) as f:
            log_contents = f.read()
        self.assertRegex(
            log_contents,
            r'\+\+\+ Unicon plugin nxos/n5k( \(unicon\.plugins\.nxos\.n5k\))? \+\+\+'
        )

    def test_learn_tokens_with_show_inventory(self):
        # Set up device to use correct mock_device data
        self.dev.connections.cli.command = \
            "mock_device_cli --os generic --state iosxe_login2"

        # Test connection succeeds and tokens learned
        self.dev.connect(learn_tokens=True, learn_hostname=True)
        self.assertEqual(self.dev.os, 'iosxe')
        self.assertEqual(self.dev.version, '15.2')
        self.assertEqual(self.dev.platform, 'cat5k')
        self.assertEqual(self.dev.model, 'c5000')
        self.assertEqual(self.dev.pid, 'WS-C5002')

        # Test that connection was redirected to the corresponding plugin
        with open(self.dev.logfile) as f:
            log_contents = f.read()
        self.assertRegex(
            log_contents,
            r'\+\+\+ Unicon plugin iosxe( \(unicon\.(internal\.)?plugins\.iosxe\))? \+\+\+'
        )

    def test_linux_learn_tokens(self):
        self.dev.connections.cli.command = \
            "mock_device_cli --os generic --state connect_ssh"

        # Test connection succeeds and tokens learned
        self.dev.connect(learn_tokens=True)
        self.assertEqual(self.dev.os, 'linux')
        self.assertEqual(self.dev.version, '4.18.0-240.22.1.el8_3.x86_64')

        # Test that connection was redirected to the corresponding plugin
        with open(self.dev.logfile) as f:
            log_contents = f.read()
        self.assertRegex(
            log_contents,
            r'\+\+\+ Unicon plugin linux( \(unicon(\.internal)?\.plugins\.linux\))? \+\+\+'
        )

    def test_iosxr_learn_tokens(self):
        # Set up device to use correct mock_device data
        self.dev.connections.cli.command = \
            "mock_device_cli --os generic --state iosxr_login"

        # Test connection succeeds and tokens learned
        self.dev.connect(learn_tokens=True, learn_hostname=True)
        self.assertEqual(self.dev.os, 'iosxr')
        self.assertEqual(self.dev.os_flavor, 'lnt')
        self.assertEqual(self.dev.version, '5.2.3.12i')
        self.assertEqual(self.dev.platform, 'iosxrv')

        # Test that connection was redirected to the corresponding plugin
        with open(self.dev.logfile) as f:
            log_contents = f.read()
        self.assertRegex(
            log_contents,
            r'\+\+\+ Unicon plugin iosxr/iosxrv( \(unicon\.plugins\.iosxr\.iosxrv\))? \+\+\+'
        )


class TestAbstractTokenDiscoveryStandardization(unittest.TestCase):
    """ Run unit testing on AbstractTokenDiscovery.standardize_tokens()
    """

    def setUp(self) -> None:
        self.mock_con = MagicMock()
        self.testbed = """
devices:
    R1:
        credentials:
            default:
                username: cisco
                password: cisco
        connections:
            defaults:
                class: unicon.Unicon
            cli:
                command: ""
                settings:
                    POST_DISCONNECT_WAIT_SEC: 0
                    GRACEFUL_DISCONNECT_WAIT_SEC: 0.2
                    INIT_EXEC_COMMANDS: []
                    INIT_CONFIG_COMMANDS: []
                    SLEEP_PRE_LAUNCH: 0.2
        """
        self.tb = load(self.testbed)
        self.dev = self.tb.devices.R1


    def test_version_standardization(self):
        discovery = AbstractTokenDiscovery(self.mock_con)

        tokens_to_test = [
            {'before':'17.7(3)Ab', 'after':'17.7.3ab'},
            {'before':'17.7.2(19700101:12345)', 'after':'17.7.2'},
            {'before':'1.4.0', 'after':'1.4'},
            {'before':'6.0(2)U6(5b)', 'after':'6.0.2u6.5b'},
            {'before':'03.03.02.SG', 'after':'3.3.2.sg'},
            {'before':'7.3(5)N1(1)', 'after':'7.3.5n1.1'},
        ]

        for tokens in tokens_to_test:
            standardized_tokens = \
                discovery.standardize_token_values({'version':tokens['before']})
            self.assertEqual(tokens['after'], standardized_tokens['version'])


    # Make sure pid's don't get put in lower case
    def test_pid_standardization(self):
        discovery = AbstractTokenDiscovery(self.mock_con)
        standardized_tokens = \
            discovery.standardize_token_values({'pid':'QWERTY12345'})
        self.assertEqual('QWERTY12345', standardized_tokens['pid'])

        # Test that white spaces are removed
        standardized_tokens = \
            discovery.standardize_token_values({'platform':'Q WE RTY    12345'})
        self.assertEqual('qwerty12345', standardized_tokens['platform'])


class TestAbstractTokenDiscoveryMisc(unittest.TestCase):
    """ Run unit testing on AbstractTokenDiscovery args, settings, etc.
    """

    def setUp(self) -> None:
        self.mock_con = MagicMock()
        self.testbed = """
devices:
    R1:
        os: generic
        credentials:
            default:
                username: cisco
                password: cisco
        connections:
            defaults:
                class: unicon.Unicon
            cli:
                command: ""
                settings:
                    POST_DISCONNECT_WAIT_SEC: 0
                    GRACEFUL_DISCONNECT_WAIT_SEC: 0.2
                    INIT_EXEC_COMMANDS: []
                    INIT_CONFIG_COMMANDS: []
                    SLEEP_PRE_LAUNCH: 0.2
        """
        self.tb = load(self.testbed)
        self.dev = self.tb.devices.R1
        self.mock_con.device = self.dev


    # Test that token discovery can be disabled using the learn_tokens boolean
    @patch('unicon.plugins.utils.AbstractTokenDiscovery.learn_device_tokens')
    def test_learn_tokens_argument(self, mock_call):
        # make sure the learn_device_tokens func is never called if set to false
        self.dev.connections.cli.command = \
            "mock_device_cli --os generic --state iosxe_enable"
        self.dev.connect()
        mock_call.assert_not_called()

    def test_assign_tokens(self):
        self.dev.os = 'generic'
        self.dev.version = '0'
        self.dev.platform = 'shoes'
        self.dev.pid = 'J0HN-VVICK'
        discovery = AbstractTokenDiscovery(self.mock_con)

        # Test that values are not overwritten by default and that learned
        # tokens get applied if a tokens prefeined value is 'generic' or is
        # non existent
        discovery.learned_tokens = {
            'os': 'ios',
            'version': 'asdasd',
            'platform': 'asdasd',
            'model': 'asdasd',
            'pid': 'asdasd',
        }
        discovery.assign_tokens(overwrite_testbed_tokens=False)
        self.assertEqual(self.dev.os, 'ios')
        self.assertEqual(self.dev.version, '0')
        self.assertEqual(self.dev.platform, 'shoes')
        self.assertEqual(self.dev.model, 'asdasd')
        self.assertEqual(self.dev.pid, 'J0HN-VVICK')

        # Test that values are overwritten if specified
        discovery.learned_tokens = {
            'os': 'overwrite1',
            'version': 'overwrite2',
            'platform': 'overwrite3',
            'model': 'overwrite4',
            'pid': 'overwrite5',
        }
        discovery.assign_tokens(overwrite_testbed_tokens=True)
        self.assertEqual(self.dev.os, 'overwrite1')
        self.assertEqual(self.dev.version, 'overwrite2')
        self.assertEqual(self.dev.platform, 'overwrite3')
        self.assertEqual(self.dev.model, 'overwrite4')
        self.assertEqual(self.dev.pid, 'overwrite5')


    def test_pid_token_lookup(self):
        discovery = AbstractTokenDiscovery(self.mock_con)
        tokens = discovery.lookup_tokens_using_pid('ASR1001-2XOC3POS')
        self.assertDictEqual({
            'pid': 'ASR1001-2XOC3POS',
            'os': 'iosxe',
            'platform': 'asr1k',
            'model': 'asr1000'
        },
        tokens)

        tokens = discovery.lookup_tokens_using_pid('N9K-C9508')
        self.assertDictEqual({
            'pid': 'N9K-C9508',
            'os': 'nxos',
            'platform': 'n9k',
            'model': 'n9500'
        },
        tokens)

    def test_pid_file_sorted(self):
        token_csv_file = os.path.join(
            Path(os.path.realpath(__file__)).parents[1],
            os.path.join('pid_tokens.csv')
        )
        pid_data = load_token_csv_file(token_csv_file)
        keys = list(pid_data.keys())
        sorted_keys = sorted(pid_data.keys())
        self.assertListEqual(keys, sorted_keys, msg=
            "All rows in the pid_tokens.csv file must be in ascending sorted "
            "order based on PID (first column)")


class TestAbstractTokenDiscoveryHAConnection(unittest.TestCase):

    def test_learn_token_HA(self):
        md = MockDeviceTcpWrapperGeneric(port=0,
                                         state='asr_exec_standby, asr_login')
        md.start()

        testbed = """
        devices:
          Router:
            os: nxos
            platform: n9k
            tacacs:
                username: cisco
            passwords:
                tacacs: cisco
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
                settings:
                    POST_DISCONNECT_WAIT_SEC: 0
                    GRACEFUL_DISCONNECT_WAIT_SEC: 0.2
                    LEARN_DEVICE_TOKENS: True
                    OVERWRITE_TESTBED_TOKENS: True
                arguments:
                    learn_tokens: True
              b:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
                settings:
                    POST_DISCONNECT_WAIT_SEC: 0
                    GRACEFUL_DISCONNECT_WAIT_SEC: 0.2
                    LEARN_DEVICE_TOKENS: True
                    OVERWRITE_TESTBED_TOKENS: True
                arguments:
                    learn_tokens: True
        """.format(md.ports[0], md.ports[1])
        tb = load(testbed)
        dev = tb.devices.Router
        try:
            dev.connect(init_config_commands=[],
                        connection_timeout=60)
            dev.disconnect()
        finally:
            md.stop()
            self.assertEqual(dev.os, 'iosxe')
            self.assertEqual(dev.version, '16.7')
            self.assertEqual(dev.platform, 'asr1k')
            self.assertEqual(dev.model, 'asr1000')
            self.assertEqual(dev.pid, 'ASR1006')


class TestUtils(unittest.TestCase):

    def test_load_token_csv_file(self):
        self.maxDiff = None
        lookup_file = os.path.join(
            Path(os.path.realpath(__file__)).parents[1],
            os.path.join('pid_tokens.csv')
        )

        # Test default behavior
        data = load_token_csv_file(file_path=lookup_file)
        for name, item in data.items():
            for key in ('os', 'platform', 'model', 'submodel'):
                self.assertIn(key, item, f'{key} not in {name} after loading')

if __name__ == "__main__":
    unittest.main()
