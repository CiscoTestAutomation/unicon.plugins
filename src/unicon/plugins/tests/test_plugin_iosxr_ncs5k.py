"""
Unittests for IOSXR plugin

Uses the mock_device.py script to test IOSXR plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import re
import os
import unittest
from unittest.mock import Mock, patch

import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestIosXrNcs5kPlugin(unittest.TestCase):

    def test_connect(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxr --state ncs5k_enable'],
                            os='iosxr',
                            series='ncs5k',
                            username='lab')
        c.connect()
        self.assertEqual(c.spawn.match.match_output,'end\r\nRP/0/RP0/CPU0:Router#')


    def test_reload(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxr --state ncs5k_enable'],
                            os='iosxr',
                            series='ncs5k',
                            username='lab')
        c.connect()
        c.reload()
        self.assertEqual(c.spawn.match.match_output,'\r\nRP/0/RP0/CPU0:Router#\r\nRP/0/RP0/CPU0:Router#')


    def test_reload_credentials(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxr --state ncs5k_enable'],
                            os='iosxr',
                            series='ncs5k',
                            credentials=dict(default=dict(
                                username='lab', password='lab')))
        c.connect()
        c.reload()
        self.assertEqual(c.spawn.match.match_output,'\r\nRP/0/RP0/CPU0:Router#\r\nRP/0/RP0/CPU0:Router#')


    def test_reload_credentials_nondefault(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxr --state ncs5k_enable'],
                            os='iosxr',
                            series='ncs5k',
                            credentials=dict(default=dict(
                                username='lab', password='lab'),
                                alt=dict(
                                username='lab2', password='lab2')))
        c.connect()
        c.reload(reload_command="reload2", reload_creds='alt')
        self.assertEqual(c.spawn.match.match_output,'\r\nRP/0/RP0/CPU0:Router#\r\nRP/0/RP0/CPU0:Router#')

    def test_reload_vty(self):
        c = Connection(hostname='Router',
                            start=['mock_device_cli --os iosxr --state ncs5k_enable_vty'],
                            os='iosxr',
                            series='ncs5k',
                            username='lab',
                            password='lab')
        c.connect()
        c.settings.RELOAD_WAIT=2
        c.reload()
        self.assertEqual(c.spawn.match.match_output,'end\r\nRP/0/RP0/CPU0:Router#')


if __name__ == "__main__":
    unittest.main()

