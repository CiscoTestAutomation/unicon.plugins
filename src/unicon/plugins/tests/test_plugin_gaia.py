'''
Tests for Unicon Gaia Plugin

Author: Sam Johnson
Contact: samuel.johnson@gmail.com
https://github.com/TestingBytes

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

import os
import unittest
import yaml
import re

from unicon import Connection
from unicon.mock.mock_device import mockdata_path
from unicon.core.errors import SubCommandFailure

with open(os.path.join(mockdata_path, 'gaia/gaia_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestGaiaPluginClish(unittest.TestCase):
    """ Tests Gaia device configured to login to clish mode
    """

    @classmethod
    def setUpClass(cls):

        cls.c = Connection(
            hostname='gaia-gw',
            start=['mock_device_cli --os gaia --state login'],
            os='gaia',
            credentials={
                'default': {
                    'username': 'gaia-user',
                    'password': 'gaia-password'
                    },
                'expert': {
                    'password': 'gaia-expert-pass'
                    }
                }
            )

        cls.c.connect()

    def test_execute(self):
        self.c.switchto('clish')
        response = self.c.execute('show version all')
        response = re.sub(r"\r\n", "\n", response)
        mock_data_response = mock_data['clish']['commands']['show version all']['response'].strip()
        self.assertEqual(response, mock_data_response)

        # check hostname
        self.assertIn("gaia-gw", self.c.hostname)

    def test_ping(self):
        response = self.c.ping('192.168.1.1')
        self.assertIn("PING 192.168.1.1 (192.168.1.1) 56(84) bytes of data.", response)

    def test_traceroute(self):
        response = self.c.traceroute('192.168.1.1')
        self.assertIn("traceroute to 192.168.1.1 (192.168.1.1), 30 hops max, 40 byte packets", response)

    def test_state_transitions(self):
        sm = self.c.state_machine
        self.assertIn("clish", sm.current_state)

        self.c.switchto('expert')
        self.assertIn("expert", sm.current_state)

        self.c.switchto('clish')
        self.assertIn("clish", sm.current_state)

    def test_error_patterns(self):

        self.c.switchto('clish')
        with self.assertRaises(SubCommandFailure):
            self.c.execute('asdf')

        self.c.switchto('expert')
        with self.assertRaises(SubCommandFailure):
            self.c.execute('asdf')


class TestGaiaPluginExpert(unittest.TestCase):
    """ Tests Gaia device configured to login to expert mode
    """

    @classmethod
    def setUpClass(cls):

        cls.c = Connection(
            hostname='gaia-gw',
            start=['mock_device_cli --os gaia --state exp_login'],
            os='gaia',
            credentials={
                'default': {
                    'username': 'gaia-user',
                    'password': 'gaia-password'
                    }
                }
            )

        cls.c.connect()

        # state should automatically change to clish on connect
        assert cls.c.state_machine.current_state == 'clish'

    def test_execute(self):
        response = self.c.execute('show version all')
        self.assertIn("Product version", response)

        # check hostname
        self.assertIn("gaia-gw", self.c.hostname)

    def test_ping(self):
        response = self.c.ping('192.168.1.1')
        self.assertIn("PING 192.168.1.1 (192.168.1.1) 56(84) bytes of data.", response)

    def test_traceroute(self):
        response = self.c.traceroute('192.168.1.1')
        self.assertIn("traceroute to 192.168.1.1 (192.168.1.1), 30 hops max, 40 byte packets", response)

    def test_state_transitions(self):
        sm = self.c.state_machine
        self.assertIn("clish", sm.current_state)

        self.c.switchto('expert')
        self.assertIn("expert", sm.current_state)

        self.c.switchto('clish')
        self.assertIn("clish", sm.current_state)


if __name__ == "__main__":
    unittest.main()
