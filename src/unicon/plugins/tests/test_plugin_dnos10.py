import os
import yaml
import unittest

from unicon import Connection
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path
import pdb;pdb.set_trace()

with open(os.path.join(mockdata_path, 'dnos10/dnos10_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestDnos10PluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='OS10',
                        start=['mock_device_cli --os dnos10 --state exec'],
                        os='dnos10',
                        username='knox',
                        tacacs_password='dell1111')
        c.connect()
        self.assertIn('OS10#', c.spawn.match.match_output)

    def test_login_connect_ssh(self):
        c = Connection(hostname='OS10',
                        start=['mock_device_cli --os dnos10 --state connect_ssh'],
                        os='dnos10',
                        username='knox',
                        tacacs_password='dell1111')
        c.connect()
        self.assertIn('OS10#', c.spawn.match.match_output)

    def test_login_connect_connectReply(self):
        c = Connection(hostname='OS10',
                        start=['mock_device_cli --os dnos10 --state exec'],
                        os='dnos10',
                        username='knox',
                        tacacs_password='dell1111',
                        connect_reply = Dialog([[r'^(.*?)Password:']]))
        c.connect()
        self.assertIn("^(.*?)Password:", str(c.connection_provider.get_connection_dialog()))
        c.disconnect()

class TestDnos10PluginExecute(unittest.TestCase):

    def test_execute_show_feature(self):
        c = Connection(hostname='OS10',
                        start=['mock_device_cli --os dnos10 --state exec'],
                        os='dnos10',
                        username='knox',
                        tacacs_password='dell1111',
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        c.connect()
        cmd = 'show ip interface brief'
        expected_response = mock_data['exec']['commands'][cmd].strip()
        ret = c.execute(cmd).replace('\r', '')
        self.assertIn(expected_response, ret)

if __name__ == "__main__":
    unittest.main()
