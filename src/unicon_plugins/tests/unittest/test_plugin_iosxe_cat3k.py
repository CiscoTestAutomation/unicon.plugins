"""
Unittests for iosxe/cat3k plugin
"""

import unittest

from unicon import Connection


class TestIosXeCat3kPluginRommonBoot(unittest.TestCase):

    def test_boot_from_rommon(self):
        d = Connection(hostname='Router',
                        start=['mock_device_cli --os iosxe --state cat3k_rommon'],
                        os='iosxe',
                        series='cat3k',
                        username='cisco',
                        tacacs_password='cisco')
        d.connect()

    def test_boot_from_rommon_with_image(self):
        d = Connection(hostname='Router',
                        start=['mock_device_cli --os iosxe --state cat3k_rommon'],
                        os='iosxe',
                        series='cat3k',
                        username='cisco',
                        tacacs_password='cisco',
                        image_to_boot='flash:rp_super_universalk9.edison.bin')
        d.connect()


if __name__ == '__main__':
    unittest.main()
