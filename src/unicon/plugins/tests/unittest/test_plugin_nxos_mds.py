"""
Unittests for NXOS/MDS plugin

Uses the unicon.plugins.tests.mock.mock_device_ios script to test NXOS/MDS plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import re
import unittest

from unicon import Connection
from unicon.core.errors import SubCommandFailure


class TestNxosMdsPluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os nxos_mds --state exec'],
                       os='nxos',
                       series='mds',
                       username='cisco',
                       tacacs_password='cisco')
        c.connect()
        assert c.spawn.match.match_output == 'end\r\nswitch#'


class TestNxosMdsPluginShellexec(unittest.TestCase):

    def test_login_shellexec(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os nxos_mds --state exec'],
                       os='nxos',
                       series='mds',
                       username='cisco',
                       tacacs_password='cisco')
        c.shellexec(['ls'])
        assert c.spawn.match.match_output == 'exit\r\nswitch#'


if __name__ == "__main__":
    unittest.main()
