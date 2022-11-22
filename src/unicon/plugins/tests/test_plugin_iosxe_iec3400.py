import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from unicon.core.errors import SubCommandFailure
from unicon.eal.dialogs import Statement, Dialog

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIec3400Plugin(unittest.TestCase):

    def test_terminal_position_handler(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            platform='iec3400'
        )
        c.connect()
        c.execute('get terminal position')
        self.assertEqual(c.spawn.match.match_output, '^[[0;200RPE1#')
        c.disconnect()

    def test_reload_with_error_pattern(self):

        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            platform='iec3400'
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
            c.reload('active_install_add',
                    reply=install_add_one_shot_dialog,
                    error_pattern=error_pattern)
            self.assertEqual(c.reload.error_pattern, error_pattern)
        finally:
            c.disconnect()

if __name__ == '__main__':
    unittest.main()