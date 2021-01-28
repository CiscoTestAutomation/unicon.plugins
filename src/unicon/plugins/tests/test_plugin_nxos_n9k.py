"""
Unittests for NXOS/N9K plugin
Uses the unicon.plugins.tests.mock.mock_device_nxos for test.
"""
__author__ = 'Difu Hu <difhu@cisco.com>'

import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
class TestNxos9kPluginReloadService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dev = Connection(
            hostname='N93_1',
            start=['mock_device_cli --os nxos --state login3'],
            os='nxos',
            platform='n9k',
            username='cisco',
            tacacs_password='cisco',
            enable_password='cisco'
        )

    def test_reload_boot_image_succeed(self):
        self.dev.connect()
        self.dev.reload(image_to_boot='ISSUCleanGolden.system.gbin')
        self.dev.disconnect()

    def test_reload_without_boot_image_fail(self):
        self.dev.connect()
        with self.assertRaises(SubCommandFailure):
            self.dev.reload()
        self.dev.disconnect()

    def test_reload_with_wrong_boot_image_fail(self):
        self.dev.connect()
        with self.assertRaises(SubCommandFailure):
            self.dev.reload(image_to_boot='WrongImage.system.gbin')
        self.dev.disconnect()


if __name__ == "__main__":
    unittest.main()
