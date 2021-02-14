'''
Tests for Unicon Gaia Plugin

Author: Sam Johnson
Contact: samuel.johnson@gmail.com
https://github.com/TestingBytes

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

import os
import yaml
import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'gaia/gaia_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestGaiaPlugin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='gaia-gw',
                        start=['mock_device_cli --os gaia --state login'],
                        os='gaia',
                        credentials={'default': {'username':'gaia-user', 'password':'gaia-password'}}
                        )

        cls.c.connect()

    def test_execute(self):
        response = self.c.execute('show version all')
        self.assertIn("Product version", response)

        # check hostname
        self.assertIn("gaia-gw", self.c.hostname)

        self.c.disconnect()

if __name__ == "__main__":
    unittest.main()
