import os
import yaml
import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'hp_comware/hp_comware_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestHPComwarePluginConnect(unittest.TestCase):

    def test_exec_prompt(self):
        hostname = "Device"
        c = Connection(hostname=hostname,
                       start=[f"mock_device_cli --os hp_comware --state exec --hostname {hostname}"],
                       os='hp_comware',
                       username='admin',
                       password='developer')
        c.connect()
        self.assertIn(f"<{hostname}>", c.spawn.match.match_output)

    def test_login_connect_ssh(self):
        hostname = "Device"
        c = Connection(hostname=hostname,
                       start=[f"mock_device_cli --os hp_comware --state connect_ssh  --hostname {hostname}"],
                       os='hp_comware',
                       username='admin',
                       line_password='developer')
        c.connect()
        self.assertIn(f"<{hostname}>", c.spawn.match.match_output)


class TestDellPluginExecute(unittest.TestCase):

    def test_execute_show_feature(self):
        hostname = "Device"
        c = Connection(hostname=hostname,
                       start=[f"mock_device_cli --os hp_comware --state exec --hostname {hostname}"],
                       os='hp_comware',
                       username='admin',
                       password='developer',
                       init_exec_commands=[],
                       init_config_commands=[]
                       )
        c.connect()
        cmd = 'display version'
        expected_response = mock_data['exec']['commands'][cmd].strip()
        ret = c.execute(cmd).replace('\r', '')
        self.assertIn(expected_response, ret)
    
    def test_execute_save(self):
        hostname = "Device"
        c = Connection(hostname=hostname,
                       start=[f"mock_device_cli --os hp_comware --state exec --hostname {hostname}"],
                       os='hp_comware',
                       username='admin',
                       password='developer',
                       init_exec_commands=[],
                       init_config_commands=[]
                       )
        c.connect()
        cmd = 'save'
        ret = c.execute(cmd).replace('\r', '')
        self.assertIn(f"<{hostname}>", c.spawn.match.match_output)


if __name__ == "__main__":
    unittest.main()

