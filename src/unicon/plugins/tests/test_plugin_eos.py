'''
Author: Richard Day
Contact: https://www.linkedin.com/in/richardday/, https://github.com/rich-day

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

import os
import yaml
import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'eos/eos_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestEOSPluginConnect(unittest.TestCase):

    def test_exec_prompt(self):
        hostname = "Switch"
        c = Connection(hostname=hostname,
                       start=["mock_device_cli --os eos --state exec --hostname {hostname}"\
                              .format(hostname=hostname)],
                       os='eos',
                       username='admin',
                       password='admin')
        c.connect()
        self.assertIn("{hostname}".format(hostname=hostname),
                      c.spawn.match.match_output)

class TestEOSPluginExecute(unittest.TestCase):

    def test_execute_show_feature(self):
        hostname = "Switch"
        c = Connection(hostname=hostname,
                       start=["mock_device_cli --os eos --state exec --hostname {hostname}"\
                              .format(hostname=hostname)],
                       os='eos',
                       username='admin',
                       password='admin',
                       init_exec_commands=[],
                       init_config_commands=[]
                       )
        c.connect()
        cmd = 'show version'
        expected_response = mock_data['exec']['commands'][cmd].strip()
        ret = c.execute(cmd).replace('\r', '')
        self.assertIn(expected_response, ret)

if __name__ == "__main__":
    unittest.main()