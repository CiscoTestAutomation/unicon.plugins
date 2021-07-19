"""
Unittests for fxos plugin

Uses the unicon.mock.mock_device script to test the plugin.

"""

__author__ = "dwapstra"

import unittest

from unicon import Connection
from unicon.eal.dialogs import Dialog
from unicon.core.errors import SubCommandFailure
from unicon.plugins.generic.statements import GenericStatements

generic_statements = GenericStatements()
password_stmt = generic_statements.password_stmt
escape_char_stmt = generic_statements.escape_char_stmt


class TestFxosPlugin(unittest.TestCase):
    def test_connect(self):
        c = Connection(hostname='Firepower',
                       start=['mock_device_cli --os fxos --state fxos_console'],
                       os='fxos',
                       platform='ftd',
                       username='cisco',
                       tacacs_password='cisco')
        c.connect()
        self.assertEqual(c.spawn.match.match_output, '\r\nFirepower# ')
        return c

    def test_execute_scope(self):
        c = self.test_connect()
        c.execute(['scope system', 'scope services', 'create ntp-server 192.168.200.101', 'commit-buffer'],
                  allow_state_change=True)
        self.assertEqual(c.spawn.match.match_output, 'commit-buffer\r\nFirepower /system/services # ')

    def test_execute_scope2(self):
        c = self.test_connect()
        c.execute(['scope service-profile'], allow_state_change=True)

    def test_console_execute(self):
        c = Connection(hostname='Firepower',
                       start=['mock_device_cli --os fxos --state chassis_exec'],
                       os='fxos',
                       platform='ftd',
                       username='cisco',
                       tacacs_password='cisco',
                       enable_password='cisco',
                       line_password='cisco')
        c.connect()
        c.execute(['connect module 1 console', 'connect ftd', 'expert', 'sudo su -'],
                  allow_state_change=True,
                  reply=Dialog([password_stmt, escape_char_stmt]))


class TestFxosPluginSystemServicesExec(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Firepower',
                           start=['mock_device_cli --os fxos --state fxos_system_services'],
                           os='fxos',
                           platform='ftd',
                           username='cisco',
                           tacacs_password='cisco',
                           enable_password='cisco',
                           line_password='cisco')
        cls.c.connect()

    def test_execute_error(self):
        for cmd in ['commit-buffer', 'show foo', 'show chassis inventory 1 fa']:
            with self.assertRaises(SubCommandFailure):
                self.c.execute(cmd)


if __name__ == "__main__":
    unittest.main()
