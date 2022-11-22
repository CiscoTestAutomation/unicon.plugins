import os
import yaml
import unittest

from unicon import Connection
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path
from unicon.core.errors import SubCommandFailure,UniconAuthenticationError
with open(os.path.join(mockdata_path, 'hvrp/hvrp_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestHuaweiVrpPluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='ooo-gg-9999zz-99',
                        start=['mock_device_cli --os hvrp --state exec'],
                        os='hvrp',
                         credentials={'default': {'username': 'nielsvanhooy', 'password': 'kpn'}})
        c.connect()
        self.assertIn('<ooo-gg-9999zz-99>', c.spawn.match.match_output)
        c.disconnect()

    def test_login_connect_ssh(self):
        c = Connection(hostname='ooo-gg-9999zz-99',
                        start=['mock_device_cli --os hvrp --state connect_ssh'],
                        os='hvrp',
                         credentials={'default': {'username': 'nielsvanhooy', 'password': 'kpn'}})
        c.connect()
        self.assertIn('<ooo-gg-9999zz-99>', c.spawn.match.match_output)
        c.disconnect()

    def test_login_connect_connectReply(self):
        c = Connection(hostname='ooo-gg-9999zz-99',
                        start=['mock_device_cli --os hvrp --state exec'],
                        os='hvrp',
                         credentials={'default': {'username': 'nielsvanhooy', 'password': 'kpn'}},
                        connect_reply = Dialog([[r'^(.*?)Password:']]))
        c.connect()
        self.assertIn("^(.*?)Password:", str(c.connection_provider.get_connection_dialog()))
        c.disconnect()

class TestHuaweiVrpPluginExecute(unittest.TestCase):

    def test_execute_show_feature(self):
        c = Connection(hostname='ooo-gg-9999zz-99',
                        start=['mock_device_cli --os hvrp --state exec'],
                        os='hvrp',
                         credentials={'default': {'username': 'nielsvanhooy', 'password': 'kpn'}},
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        c.connect()
        cmd = 'display version'
        expected_response = mock_data['exec']['commands'][cmd].strip()
        ret = c.execute(cmd).replace('\r', '')
        self.assertIn(expected_response, ret)
        c.disconnect()

    def test_execute_unsupported(self):
        c = Connection(hostname='ooo-gg-9999zz-99',
                        start=['mock_device_cli --os hvrp --state exec'],
                        os='hvrp',
                         credentials={'default': {'username': 'nielsvanhooy', 'password': 'kpn'}},
                        init_exec_commands=[],
                        init_config_commands=[]
                        )
        c.connect()
        self.assertRaises(SubCommandFailure,c.execute,"display vresion")
        c.disconnect()

class TestHuaweiVrpPluginConfigure(unittest.TestCase):

    def test_config(self):
        c = Connection(hostname='ooo-gg-9999zz-99',
                        start=['mock_device_cli --os hvrp --state exec'],
                        os='hvrp',
                        credentials={'default': {'username': 'nielsvanhooy', 'password': 'kpn'}},
                        init_config_commands=[]
                        )
        c.connect()
        c.configure(["bgp 65000","peer 1.1.1.1 as-number 64666"])
        c.disconnect()

    def test_unsupported_config(self):
        c = Connection(hostname='ooo-gg-9999zz-99',
                        start=['mock_device_cli --os hvrp --state exec'],
                        os='hvrp',
                        credentials={'default': {'username': 'nielsvanhooy', 'password': 'kpn'}},
                        init_config_commands=[]
                        )
        c.connect()
        self.assertRaises(SubCommandFailure,c.configure,"bpg 65000")
        c.disconnect()

if __name__ == "__main__":
    unittest.main()
