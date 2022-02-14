import unittest
from unittest.mock import patch

import unicon
from unicon import Connection

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
