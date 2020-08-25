"""
Unittests for IOSXR ASR9K HA plugin

Uses the mock_device.py script to test IOSXR plugin.

"""

__author__ = "Takashi Higashimura <tahigash@cisco.com>"

import unittest
from time import sleep

from unicon import Connection
from pyats.topology import loader

from unicon.plugins.tests.mock.mock_device_iosxr import MockDeviceTcpWrapperIOSXR


class TestIOSXRPluginHAConnect(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperIOSXR(port=0, state='login,console_standby')
        cls.md.start()

        cls.testbed = """
        devices:
          Router:
            os: iosxr
            series: asr9k
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
                  POST_HA_RELOAD_CONFIG_SYNC_WAIT: 30
                  IOSXR_INIT_EXEC_COMMANDS: []
                  IOSXR_INIT_CONFIG_COMMANDS: []
                  HA_INIT_CONFIG_COMMANDS: []
              b:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
                settings:
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
            series: asr9k
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
