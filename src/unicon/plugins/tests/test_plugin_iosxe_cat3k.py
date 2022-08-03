"""
Unittests for iosxe/cat3k plugin
"""

import unittest

import unicon
from unicon import Connection
from unicon.plugins.tests.mock.mock_device_iosxe import MockDeviceTcpWrapperIOSXE
from unicon.core.errors import SubCommandFailure
from unicon.eal.dialogs import Statement, Dialog

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXeCat3kPlugin(unittest.TestCase):

    def test_boot_from_rommon(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='cat3k_rommon')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            platform='cat3k',
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

    def test_reload_via_rommon(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='cat3k_enable_reload_to_rommon')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            platform='cat3k',
            credentials=dict(default=dict(username='cisco', password='cisco')),
            log_buffer=True,
            mit=True
        )
        try:
            c.connect()
            c.reload()
            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()
            md.stop()

    def test_reload_with_error_pattern(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='cat3k_login')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            platform='cat3k',
            credentials=dict(default=dict(username='cisco', password='cisco')),
            log_buffer=True,
            mit=True
        )
        install_add_one_shot_dialog = Dialog([
                 Statement(pattern=r"FAILED:.* ",
                           action=None,
                           loop_continue=False,
                           continue_timer=False),
         ])
        error_pattern=[r"FAILED:.* ",]

        try:
            c.connect()
            c.settings.POST_RELOAD_WAIT = 1
            with self.assertRaises(SubCommandFailure):
                c.reload('active_install_add',
                          reply=install_add_one_shot_dialog,
                          error_pattern=error_pattern)
            self.assertEqual(c.reload.error_pattern, error_pattern)

        finally:
            c.disconnect()
            md.stop()



if __name__ == '__main__':
    unittest.main()
