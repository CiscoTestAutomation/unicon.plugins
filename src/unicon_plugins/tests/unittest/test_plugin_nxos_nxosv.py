"""
Unittests for NXOS/NXOSv plugin

Uses the mock_device.py script to test the plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import re
import unittest

from unicon import Connection
from unicon.core.errors import SubCommandFailure


class TestNxosNxosvPluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='switch',
                        start=['mock_device_cli --os nxos --state exec'],
                        os='nxos',
                        series='nxosv',
                        username='cisco',
                        tacacs_password='cisco')
        c.connect()
        assert c.spawn.match.match_output == 'end\r\nswitch# '

if __name__ == "__main__":
    unittest.main()
