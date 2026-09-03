"""
Unittests for iosxe/cat9k plugin
"""

import unittest


import unicon
from unicon import Connection

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXECat9kPluginReload(unittest.TestCase):

    def test_reload(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state c9k_vwlc_login --hostname WLC'],
                       os='iosxe',
                       platform='cat9k',
                       type='vWLC',
                       credentials=dict(default=dict(username='admin', password='cisco'),
                                        enable=dict(password='Secret12345!')),
                       learn_hostname=True,
                       log_buffer=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       debug=False)
        try:
            c.connect()
            c.settings.POST_RELOAD_WAIT = 1
            c.settings.PASSWORD_ATTEMPTS = 5
            c.reload()
            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()
