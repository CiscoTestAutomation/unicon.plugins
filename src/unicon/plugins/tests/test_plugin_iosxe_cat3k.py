"""
Unittests for iosxe/cat3k plugin
"""

import unittest

from unicon import Connection
from unicon.plugins.tests.mock.mock_device_iosxe import MockDeviceTcpWrapperIOSXE


class TestIosXeCat3kPluginRommonBoot(unittest.TestCase):

    def test_boot_from_rommon(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='cat3k_rommon')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            platform='cat3k',
            settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
            credentials=dict(default=dict(username='cisco', password='cisco')),
            log_buffer=True
        )
        try:
            c.connect()
            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()
            md.stop()

    def test_boot_from_rommon_with_image(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='cat3k_rommon')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            platform='cat3k',
            settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
            credentials=dict(default=dict(username='cisco', password='cisco')),
            image_to_boot='flash:rp_super_universalk9.edison.bin',
            log_buffer=True
        )
        try:
            c.connect()
            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()
            md.stop()


if __name__ == '__main__':
    unittest.main()
