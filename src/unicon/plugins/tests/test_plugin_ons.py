"""
Unittests for ONS plugin

"""
import os
import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure
from unicon.eal.dialogs import Dialog
from unicon.mock.mock_device import mockdata_path


unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestOnsPlugin(unittest.TestCase):

    def test_connect(self):

        c = Connection(hostname='ONS',
                       start=['mock_device_cli --os ons --state tl1'],
                       os='ons',
                       credentials=dict(default=dict(username='admin', password='admin')),
                       )
        c.connect()
        output = c.execute('help')
        self.assertEqual(output, 'command help')

    def test_connect_login_fail(self):

        c = Connection(hostname='ONS',
                       start=['mock_device_cli --os ons --state tl1'],
                       os='ons',
                       credentials=dict(default=dict(username='admin', password='test')),
                       )
        with self.assertRaises(Exception):
            c.connect()
