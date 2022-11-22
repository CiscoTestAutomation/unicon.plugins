"""
Unittests for iosxe/csr1000v/vewlc
"""

__author__ = 'Difu Hu <difhu@cisco.com>'

import unittest
from unittest.mock import patch

import unicon
from unicon import Connection


class IosXECsr1000vVewlcCopy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.d = Connection(hostname='Router',
                           start=['mock_device_cli --os iosxe --state ewlc_enable'],
                           os='iosxe',
                           platform='csr1000v',
                           model='vewlc',
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


if __name__ == '__main__':
    unittest.main()
