'''
Author: Renato Almeida de Oliveira
Contact: renato.almeida.oliveira@gmail.com
https://twitter.com/ORenato_Almeida
https://www.youtube.com/c/RenatoAlmeidadeOliveira
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

with open(os.path.join(mockdata_path, 'comware/comware_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestHPComwarePluginConnect(unittest.TestCase):

    def test_exec_prompt(self):
        hostname = "Device"
        c = Connection(hostname=hostname,
                       start=["mock_device_cli --os comware --state exec --hostname {hostname}"\
                              .format(hostname=hostname)],
                       os='comware',
                       username='admin',
                       password='developer')
        c.connect()
        self.assertIn("<{hostname}>".format(hostname=hostname),
                      c.spawn.match.match_output)

    def test_login_connect_ssh(self):
        hostname = "Device"
        c = Connection(hostname=hostname,
                       start=["mock_device_cli --os comware --state connect_ssh  --hostname {hostname}"\
                              .format(hostname=hostname)],
                       os='comware',
                       username='admin',
                       line_password='developer')
        c.connect()
        self.assertIn("<{hostname}>".format(hostname=hostname),
                      c.spawn.match.match_output)


class TestDellPluginExecute(unittest.TestCase):

    def test_execute_show_feature(self):
        hostname = "Device"
        c = Connection(hostname=hostname,
                       start=["mock_device_cli --os comware --state exec --hostname {hostname}"\
                              .format(hostname=hostname)],
                       os='comware',
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
                       start=["mock_device_cli --os comware --state exec --hostname {hostname}"\
                              .format(hostname=hostname)],
                       os='comware',
                       username='admin',
                       password='developer',
                       init_exec_commands=[],
                       init_config_commands=[]
                       )
        c.connect()
        ret = c.save().replace('\r', '')
        self.assertIn("<{hostname}>".format(hostname=hostname),
                      c.spawn.match.match_output)


    def test_execute_save_file(self):
        hostname = "Device"
        c = Connection(hostname=hostname,
                       start=["mock_device_cli --os comware --state exec --hostname {hostname}"\
                              .format(hostname=hostname)],
                       os='comware',
                       username='admin',
                       password='developer',
                       init_exec_commands=[],
                       init_config_commands=[]
                       )
        c.connect()
        ret = c.save(file_path="newfile.cfg" ).replace('\r', '')
        self.assertIn("<{hostname}>".format(hostname=hostname),
                      c.spawn.match.match_output)


    def test_execute_save_file_overwrite(self):
        hostname = "Device"
        c = Connection(hostname=hostname,
                       start=["mock_device_cli --os comware --state exec --hostname {hostname}"\
                              .format(hostname=hostname)],
                       os='comware',
                       username='admin',
                       password='developer',
                       init_exec_commands=[],
                       init_config_commands=[]
                       )
        c.connect()
        ret = c.save(file_path="oldfile.cfg", overwrite=True ).replace('\r', '')
        self.assertIn("<{hostname}>".format(hostname=hostname),
                      c.spawn.match.match_output)


if __name__ == "__main__":
    unittest.main()

