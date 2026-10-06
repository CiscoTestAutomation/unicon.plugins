"""
Unittests for Generic/IOSXE plugin

Uses the unicon.plugins.tests.mock.mock_device_ios script to test IOSXE plugin.

"""

import unittest

import unicon
from unicon import Connection
from unicon.plugins.tests.mock.mock_device_iosxe import MockDeviceTcpWrapperIOSXE


unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXESwitchover(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.md = MockDeviceTcpWrapperIOSXE(
            hostname='Router', port=0,
            state='stack_login' + ',stack_login' * 4, stack=True)
        cls.md.start()
        cls.c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(port) for port in cls.md.ports[:]],
            os='iosxe',
            chassis_type='stack',
            username='cisco',
            tacacs_password='cisco',
            enable_password='cisco'
        )
        cls.c.connect()
        cls.c.settings.POST_SWITCHOVER_SLEEP = 1

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()
        cls.md.stop()

    def test_switchover(self):
        self.c.switchover()


if __name__ == "__main__":
    unittest.main()
