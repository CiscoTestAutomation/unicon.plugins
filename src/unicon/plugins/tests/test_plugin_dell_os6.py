import os
import yaml
import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'dell_os6/dellos6_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestDellos6PluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='DellOS6',
                        start=['mock_device_cli --os dellos6 --state exec'],
                        os='dell',
                        platform='os6',
                        username='knox',
                        tacacs_password='dell1111')
        c.connect()
        self.assertIn('DellOS6#', c.spawn.match.match_output)
        c.disconnect()

    def test_login_connect_ssh(self):
        c = Connection(hostname='DellOS6',
                        start=['mock_device_cli --os dellos6 --state connect_ssh'],
                        os='dell',
                        platform='os6',
                        username='knox',
                        tacacs_password='dell1111')
        c.connect()
        self.assertIn('DellOS6#', c.spawn.match.match_output)
        c.disconnect()

    def test_login_connect_connectReply(self):
        c = Connection(hostname='DellOS6',
                        start=['mock_device_cli --os dellos6 --state exec'],
                        os='dell',
                        platform='os6',
                        username='knox',
                        tacacs_password='dell1111',
                        connect_reply = Dialog([[r'^(.*?)Password:']]))
        c.connect()
        self.assertIn("^(.*?)Password:", str(c.connection_provider.get_connection_dialog()))
        c.disconnect()

class TestDellos6PluginExecute(unittest.TestCase):

    def test_execute_show_feature(self):
        c = Connection(hostname='DellOS6',
                        start=['mock_device_cli --os dellos6 --state exec'],
                        os='dell',
                        platform='os6',
                        username='knox',
                        tacacs_password='dell1111')
        c.connect()
        cmd = 'show ip interface'
        expected_response = mock_data['exec']['commands'][cmd].strip()
        ret = c.execute(cmd).replace('\r', '')
        self.assertIn(expected_response, ret)
        c.disconnect()

if __name__ == "__main__":
    unittest.main()
