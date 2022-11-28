"""
Unittests for IOSXR ASR9K HA plugin

Uses the mock_device.py script to test IOSXR plugin.

"""

__author__ = "Takashi Higashimura <tahigash@cisco.com>"

import unittest
from time import sleep

from unicon import Connection
from unicon.eal.dialogs import Statement, Dialog
from unicon.core.errors import SubCommandFailure

from pyats.topology import loader

from unicon.plugins.tests.mock.mock_device_iosxr import MockDeviceTcpWrapperIOSXR
import unicon

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC=0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC=0.2


class TestIOSXRPluginHAConnect(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperIOSXR(port=0, state='login,console_standby')
        cls.md.start()

        cls.testbed = """
        devices:
          Router:
            os: iosxr
            platform: asr9k
            type: router
            tacacs:
                username: admin
            passwords:
                tacacs: admin
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
                settings:
                  POST_RELOAD_WAIT: 2
                  POST_HA_RELOAD_CONFIG_SYNC_WAIT: 30
                  IOSXR_INIT_EXEC_COMMANDS: []
                  IOSXR_INIT_CONFIG_COMMANDS: []
                  HA_INIT_CONFIG_COMMANDS: []
              b:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
                settings:
                  POST_RELOAD_WAIT: 2
                  POST_HA_RELOAD_CONFIG_SYNC_WAIT: 30
                  IOSXR_INIT_EXEC_COMMANDS: []
                  IOSXR_INIT_CONFIG_COMMANDS: []
                  HA_INIT_CONFIG_COMMANDS: []
        """.format(cls.md.ports[0], cls.md.ports[1])
        tb = loader.load(cls.testbed)
        cls.r = tb.devices.Router
        cls.r.connect()

    @classmethod
    def tearDownClass(self):
        self.md.stop()

    def test_execute(self):
        self.r.execute('show platform')

    def test_reload(self):
        self.r.reload(reload_command='admin hw-module location all reload', timeout=30)

    def test_reload_with_error_pattern(self):
        install_add_one_shot_dialog = Dialog([
            Statement(pattern=r"FAILED:.* ",
                      action=None,
                      loop_continue=False,
                      continue_timer=False),
           ])
        error_pattern=[r"FAILED:.* ",]

        with self.assertRaises(SubCommandFailure):
            self.r.reload('active_install_add',
                      reply=install_add_one_shot_dialog,
                      error_pattern = error_pattern)

    def test_bash_console(self):
        with self.r.bash_console() as conn:
            conn.execute('pwd')
        ret = self.r.active.spawn.match.match_output
        self.assertIn('exit', ret)
        self.assertIn('Router#', ret)

    def test_attach_console(self):
        with self.r.attach_console('0/RP0/CPU0') as conn:
            conn.execute('ls')
        ret = self.r.active.spawn.match.match_output
        self.assertIn('exit', ret)
        self.assertIn('Router#', ret)

class TestIOSXRPluginHAConnectAdmin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperIOSXR(port=0, state='login1,console_standby')
        cls.md.start()

        cls.testbed = """
        devices:
          Router:
            os: iosxr
            platform: asr9k
            type: router
            tacacs:
                username: admin
            passwords:
                tacacs: admin
            connections:
              defaults:
                class: unicon.Unicon
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
              b:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
        """.format(cls.md.ports[0], cls.md.ports[1])
        tb = loader.load(cls.testbed)
        cls.r = tb.devices.Router
        cls.r.connect()

    @classmethod
    def tearDownClass(self):
        self.md.stop()

    def test_admin_attach_console(self):

        with self.r.admin_attach_console('0/RP0') as console:
            out = console.execute('pwd')
            self.assertIn('/misc/disk1', out)
        ret = self.r.active.spawn.match.match_output
        self.assertIn('exit', ret)
        self.assertIn('Router#', ret)


if __name__ == "__main__":
    unittest.main()
