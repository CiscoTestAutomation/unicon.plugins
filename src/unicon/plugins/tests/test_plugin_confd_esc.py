"""
Unittests for ConfD/ESC plugin

Uses the mock_device.py script to test the connect, execute and configure services.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import re
import unittest

from unicon import Connection


class TestNsoPluginConnect(unittest.TestCase):

    def test_connect_cisco_exec(self):
        c = Connection(hostname='esc',
                        start=['mock_device_cli --os confd --state juniper_exec'],
                        os='confd',
                        platform='esc',
                        username='admin',
                        tacacs_password='admin')
        c.connect()

if __name__ == "__main__":
    unittest.main()
