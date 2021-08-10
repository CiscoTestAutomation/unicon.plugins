"""
Unittests for NXOS n5k plugin

Uses the unicon.plugins.tests.mock.mock_device_ios script to test NXOS plugin.

"""

__author__ = "Myles Dear <mdear@cisco.com>"

import unicon
import unittest
from unittest.mock import patch
from unicon import Connection

class TestNxosN5kPluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os nxos --state n5k_exec'],
                       os='nxos',
                       platform='n5k',
                       credentials=dict(default=dict(username='cisco',
                                        password='cisco')),
                       mit=True)
        c.connect()
        assert c.spawn.match.match_output == 'switch# '


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestNxosN5kPluginReloadService(unittest.TestCase):

    def test_reload(self):
        dev = Connection(
            hostname='',
            start=['mock_device_cli --os nxos --state n5k_exec'],
            os='nxos',
            platform='n5k',
            credentials=dict(default=dict(username='admin',
                            password='lab')),
            mit=True
        )
        dev.connect()
        dev.settings.RELOAD_RECONNECT_WAIT = 1
        dev.reload()
        dev.disconnect()

    def test_reload_credentials(self):
        dev = Connection(
            hostname='',
            start=['mock_device_cli --os nxos --state n5k_exec'],
            os='nxos',
            platform='n5k',
            credentials=dict(default=dict(
                username='admin', password='lab')),
            mit=True
        )
        dev.connect()
        dev.settings.RELOAD_RECONNECT_WAIT = 1
        dev.reload()
        dev.disconnect()

    def test_reload_credentials_nondefault(self):
        dev = Connection(
            hostname='',
            start=['mock_device_cli --os nxos --state n5k_exec'],
            os='nxos',
            platform='n5k',
            credentials=dict(default=dict(
                username='admin', password='lab'),
                alt=dict(
                username='admin', password='lab2')),
            mit=True
        )
        dev.connect()
        dev.settings.RELOAD_RECONNECT_WAIT = 1
        dev.reload(reload_command="reload2", reload_creds='alt')
        dev.disconnect()

if __name__ == "__main__":
    unittest.main()
