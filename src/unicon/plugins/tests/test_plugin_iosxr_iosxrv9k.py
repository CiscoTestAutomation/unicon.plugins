"""
Unittests for IOSXR/XRv plugin

Uses the mock_device.py script to test IOSXR plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import os
import yaml
import unittest

from unicon import Connection
from unicon.mock.mock_device import mockdata_path

with open(os.path.join(mockdata_path, 'iosxr/iosxr_mock_data.yaml'), 'rb') as datafile:
    mock_data = yaml.safe_load(datafile.read())


class TestIosXrPlugin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='iosxrv-1',
            start=['mock_device_cli --os iosxr --state iosxrv9k_connect'],
            os='iosxr',
            platform='iosxrv9k',
            username='cisco',
            enable_password='admin',
            learn_hostname=True,
            init_exec_commands=[],
            init_config_commands=[],
            connection_timeout=1,
        )

    def test_learn_hostname(self):
        self.c.settings.INITIAL_LAUNCH_WAIT_SEC=0.1
        self.c.connect()

if __name__ == "__main__":
    unittest.main()

