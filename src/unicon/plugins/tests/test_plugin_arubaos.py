import os
import yaml
import unittest

import unicon
from unicon import Connection
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'arubaos/arubaos_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestArubaosPluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='ArubaMM',
                        start=['mock_device_cli --os arubaos --state execute'],
                        os='arubaos',
                        credentials=dict(default=dict(username='admin', password='admins')))
        c.connect()
        self.assertIn('(ArubaMM) *[mynode] #', c.spawn.match.match_output)
        c.disconnect()

class TestArubaosPluginExecute(unittest.TestCase):

    def test_execute_show_feature(self):
        c = Connection(hostname='ArubaMM',
                        start=['mock_device_cli --os arubaos --state execute'],
                        os='arubaos',
                        credentials=dict(default=dict(username='admin', password='admins')),
                        init_exec_commands=[],
                        init_config_commands=[])
        c.connect()
        cmd = 'show image version'
        expected_response = mock_data['execute']['commands'][cmd].strip()
        ret = c.execute(cmd).replace('\r', '')
        self.assertIn(expected_response, ret)
        c.disconnect()

if __name__ == "__main__":
    unittest.main()
