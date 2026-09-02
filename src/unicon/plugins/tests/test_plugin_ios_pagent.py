
import unittest
from unittest.mock import Mock, call, patch

import unicon
from unicon import Connection

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosPagentPlugin(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os ios --state pagent_disable_without_license'],
                       os='ios',
                       platform='pagent',
                       username='cisco',
                       enable_password='cisco',
                       tacacs_password='cisco',
                       pagent_key='899573834241',
                       settings={
                           'POST_DISCONNECT_WAIT_SEC': 0,
                           'GRACEFUL_DISCONNECT_WAIT_SEC': 0
                       })
        c.connect()
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')
        c.disconnect()

    def test_emu_prompt(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os ios --state pagent_exec'],
                       os='ios',
                       platform='pagent',
                       init_config_commands=[],
                       init_exec_commands=[],
                       learn_hostname=True
                       )

        c.connect()
        c.execute('emu', allow_state_change=True)
        c.disconnect()
