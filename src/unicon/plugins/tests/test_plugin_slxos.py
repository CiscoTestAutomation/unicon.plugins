'''
Author: Fabio Pessoa Nunes
Contact: https://www.linkedin.com/in/fpessoanunes/

'''

import os
import yaml
import unittest
from unittest.mock import patch

from unicon import Connection
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'slxos/slxos_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestSlxosPluginConnect(unittest.TestCase):

    def test_login_connect_ssh(self):
        hostname = "SLX"
        c = Connection(hostname=hostname,
                        start=['mock_device_cli --os slxos --state connect_ssh --hostname {hostname}'
                               .format(hostname=hostname)],
                        os='slxos',
                        credentials={'default': {'username': 'admin','password': 'password'}})
        c.connect()
        self.assertIn("{hostname}#".format(hostname=hostname), c.spawn.match.match_output)
        c.disconnect()


class TestSlxosPluginExecute(unittest.TestCase):

    def test_execute_show_feature(self):
        hostname = "SLX"
        c = Connection(hostname=hostname,
                        start=['mock_device_cli --os slxos --state exec --hostname {hostname}'
                               .format(hostname=hostname)],
                        os='slxos',
                        credentials={'default': {'username': 'admin','password': 'password'}},
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        c.connect()
        cmd = 'show ip interface brief'
        expected_response = mock_data['exec']['commands'][cmd].strip()
        ret = c.execute(cmd).replace('\r', '')
        self.assertIn(expected_response, ret)
        c.disconnect()


class TestSlxosPluginConfigure(unittest.TestCase):

    def test_execute_configure(self):
        hostname = "SLX"
        c = Connection(hostname=hostname,
                        start=['mock_device_cli --os slxos --state exec --hostname {hostname}'
                               .format(hostname=hostname)],
                        os='slxos',
                        credentials={'default': {'username': 'admin','password': 'password'}},
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        c.connect()
        cmd = 'configure'
        c.execute(cmd).replace('\r', '')
        self.assertIn("{hostname}(config)#".format(hostname=hostname), c.spawn.match.match_output)
        cmd = 'end'
        c.execute(cmd).replace('\r', '')
        self.assertIn("{hostname}#".format(hostname=hostname), c.spawn.match.match_output)
        c.disconnect()

if __name__ == "__main__":
    unittest.main()
