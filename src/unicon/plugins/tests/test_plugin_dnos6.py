import os
import yaml
import unittest

import unicon
from unicon import Connection
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'dnos6/dnos6_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestDnos6PluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='DellOS6',
                        start=['mock_device_cli --os dnos6 --state exec'],
                        os='dnos6',
                        credentials=dict(default=dict(username='knox', password='dell1111')))
        c.connect()
        self.assertIn('DellOS6#', c.spawn.match.match_output)
        c.disconnect()

    def test_login_connect_ssh(self):
        c = Connection(hostname='DellOS6',
                        start=['mock_device_cli --os dnos6 --state connect_ssh'],
                        os='dnos6',
                        credentials=dict(default=dict(username='knox', password='dell1111')))
        c.connect()
        self.assertIn('DellOS6#', c.spawn.match.match_output)
        c.disconnect()

    def test_login_connect_connectReply(self):
        c = Connection(hostname='DellOS6',
                        start=['mock_device_cli --os dnos6 --state exec'],
                        os='dnos6',
                        credentials=dict(default=dict(username='knox', password='dell1111')),
                        connect_reply = Dialog([[r'^(.*?)Password:']]))
        c.connect()
        self.assertIn("^(.*?)Password:", str(c.connection_provider.get_connection_dialog()))
        c.disconnect()

class TestDnos6PluginExecute(unittest.TestCase):

    def test_execute_show_feature(self):
        c = Connection(hostname='DellOS6',
                        start=['mock_device_cli --os dnos6 --state exec'],
                        os='dnos6',
                        credentials=dict(default=dict(username='knox', password='dell1111')),
                        init_exec_commands=[],
                        init_config_commands=[])
        c.connect()
        cmd = 'show ip interface'
        expected_response = mock_data['exec']['commands'][cmd].strip()
        ret = c.execute(cmd).replace('\r', '')
        self.assertIn(expected_response, ret)
        c.disconnect()

if __name__ == "__main__":
    unittest.main()
