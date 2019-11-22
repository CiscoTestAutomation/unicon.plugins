"""
Unittests for IOSXR/XRv plugin

Uses the mock_device.py script to test IOSXR plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import os
import yaml
import unittest

import unicon
from unicon import Connection
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'iosxr/iosxr_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestIosXrPlugin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='iosxrv-1',
                            start=['mock_device_cli --os iosxr --state iosxrv_enable'],
                            os='iosxr',
                            series='iosxrv',
                            username='cisco',
                            enable_password='admin',
                            init_exec_commands=[],
                            init_config_commands=[],
                            )
        cls.c.connect()        

    def test_execute(self):
        r = self.c.execute('show platform')
        self.assertEqual(r.replace('\r', ''), mock_data['enable']['commands']['show platform'].strip())

    def test_admin(self):
        r = self.c.admin_execute('show platform')
        self.assertEqual(r.replace('\r', ''), mock_data['admin']['commands']['show platform'].strip())

    def test_admin_enable_iosxrv(self):
        c = Connection(hostname='iosxrv-1',
                            start=['mock_device_cli --os iosxr --state iosxrv_enable'],
                            os='iosxr',
                            series='iosxrv',
                            username='cisco',
                            tacacs_password='admin',
                            )
        c.connect()
        c.state_machine.go_to('admin', c.spawn)
        self.assertEqual(c.spawn.match.match_output,'admin\r\nRP/0/0/CPU0:iosxrv-1(admin)#')



if __name__ == "__main__":
    unittest.main()

