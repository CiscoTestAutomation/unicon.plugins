import os
import yaml
import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'ironware/ironware_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestIronWarePluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='mlx8',
                        start=['mock_device_cli --os ironware --state exec'],
                        os='ironware',
                        username='ironware1',
                        tacacs_password='pyatsRocks!')
        c.connect()
        self.assertIn('mlx8#', c.spawn.match.match_output)

    def test_login_connect_ssh(self):
        c = Connection(hostname='mlx8',
                        start=['mock_device_cli --os ironware --state connect_ssh'],
                        os='ironware',
                        username='ironware1',
                        tacacs_password='pyatsRocks!')
        c.connect()
        self.assertIn('mlx8#', c.spawn.match.match_output)

    def test_login_connect_connectReply(self):
        c = Connection(hostname='mlx8',
                        start=['mock_device_cli --os ironware --state exec'],
                        os='ironware',
                        username='ironware1',
                        tacacs_password='pyatsRocks!',
                        connect_reply = Dialog([[r'^(.*?)Password:']]))
        c.connect()
        self.assertIn("^(.*?)Password:", str(c.connection_provider.get_connection_dialog()))
        c.disconnect()

class TestIronWarePluginExecute(unittest.TestCase):

    def test_execute_show_feature(self):
        c = Connection(hostname='mlx8',
                        start=['mock_device_cli --os ironware --state exec'],
                        os='ironware',
                        username='ironware1',
                        tacacs_password='pyatsRocks!',
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        c.connect()
        cmd = 'show ip route'
        expected_response = mock_data['exec']['commands'][cmd].strip()
        ret = c.execute(cmd).replace('\r', '')
        self.assertIn(expected_response, ret)

if __name__ == "__main__":
    unittest.main()
