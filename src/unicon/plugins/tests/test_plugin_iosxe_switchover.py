"""
Unittests for Generic/IOSXE plugin

Uses the unicon.plugins.tests.mock.mock_device_ios script to test IOSXE plugin.

"""

import unittest

import unicon
from unicon import Connection


unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXESwitchover(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='Router',
            start = ['mock_device_cli --os iosxe --state stack_login --hostname Router']*5,
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

    def test_switchover(self):
        self.c.switchover()


if __name__ == "__main__":
    unittest.main()
