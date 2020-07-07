"""
Unittests for iosxe/cat3k/ewlc plugin
"""

__author__ = 'Difu Hu <difhu@cisco.com>'

import unittest
from unittest.mock import patch

import unicon
from unicon import Connection


class TestIosXECat3kEwlcCopy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.d = Connection(hostname='Router',
                           start=['mock_device_cli --os iosxe --state ewlc_enable'],
                           os='iosxe',
                           series='cat3k',
                           model='ewlc',
                           username='cisco',
                           tacacs_password='cisco')
        cls.d.connect()

    @classmethod
    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def tearDownClass(cls):
        cls.d.disconnect()

    def test_copy_tftp_flash(self):
        self.d.copy(source='tftp:',
                    dest='flash:',
                    server='172.18.200.210',
                    source_file='/boot/rp_super_universalk9.edison.bin',
                    dest_file='rp_super_universalk9.edison.bin')

    def test_copy_tftp_flash_vrf(self):
        self.d.copy(source='tftp:',
                    dest='flash:',
                    vrf='Mgmt-vrf',
                    server='172.18.200.210',
                    source_file='/boot/vrf_rp_super_universalk9.edison.bin',
                    dest_file='vrf_rp_super_universalk9.edison.bin')

class TestIosXECat3kEwlcConfigure(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.d = Connection(hostname='Router',
                           start=['mock_device_cli --os iosxe --state ewlc_enable'],
                           os='iosxe',
                           series='cat3k',
                           model='ewlc',
                           username='cisco',
                           tacacs_password='cisco')
        cls.d.connect()

    @classmethod
    @patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
    @patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0.2)
    def tearDownClass(cls):
        cls.d.disconnect()

    def test_config_with_prompt(self):
        self.d.configure("wlan shutdown")

class TestIosXECat3kEwlcStandbyReload(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.d = Connection(hostname='Router',
                           start=['mock_device_cli --os iosxe --state ewlc_enable'],
                           os='iosxe',
                           series='cat3k',
                           model='ewlc',
                           username='cisco',
                           tacacs_password='cisco')
        cls.d.connect()

    def test_reset_standby(self):
        r = self.d.execute('redundancy reload peer')


class TestIosXeCat3kEwlcPluginRecoveryMode(unittest.TestCase):

    def test_boot_from_rommon_with_image(self):
        d = Connection(hostname='Router',
                        start=['mock_device_cli --os iosxe --state ewlc_exec_recovery_mode'],
                        os='iosxe',
                        series='cat3k',
                        init_config_commands=[])
        d.connect()


if __name__ == '__main__':
    unittest.main()
