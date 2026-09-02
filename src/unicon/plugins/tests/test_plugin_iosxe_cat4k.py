"""
Unittests for iosxe/cat4k plugin
"""

import unittest

import unicon
from unicon import Connection
from unicon.plugins.tests.mock.mock_device_iosxe_cat4k import MockDeviceTcpWrapperIOSXECat4k
from unicon.core.errors import SubCommandFailure


unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXeCat4kPlugin(unittest.TestCase):

    def test_connect(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state c4k_login'],
                       os='iosxe',
                       platform='cat4k',
                       credentials=dict(default=dict(username='admin', password='cisco')),
                       settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
                       log_buffer=True
                       )
        d.connect()
        d.disconnect()



# class TestIosXECat4kPluginReload(unittest.TestCase):
#     def test_reload(self):
#         md = MockDeviceTcpWrapperIOSXECat4k(port=0, state='c4k_login, cat4k_locked')
#         md.start()

#         c = Connection(
#             hostname='switch',
#             start=[
#                 'telnet 127.0.0.1 {}'.format(md.ports[0]),
#                 'telnet 127.0.0.1 {}'.format(md.ports[1]),
#             ],
#             os='iosxe',
#             platform='cat4k',
#             settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
#             credentials=dict(default=dict(username='admin', password='cisco'),)
#         )
#         try:
#             c.connect()
#             c.settings.POST_RELOAD_WAIT = 1
#             c.reload()
#             self.assertEqual(c.state_machine.current_state, 'enable')
#         finally:
#             c.disconnect()
#             md.stop()
class TestIosXECat4kPluginExecute(unittest.TestCase):
    def test_execute(self):
        md = MockDeviceTcpWrapperIOSXECat4k(port=0, state='c4k_login, cat4k_locked')
        md.start()

        c = Connection(
            hostname='switch',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1]),
            ],
            os='iosxe',
            platform='cat4k',
            settings=dict(POST_DISCONNECT_WAIT_SEC=0, GRACEFUL_DISCONNECT_WAIT_SEC=0.2),
            credentials=dict(default=dict(username='admin', password='cisco'),)

        )
        try:
            c.connect()
            c.settings.POST_RELOAD_WAIT = 1
            with self.assertRaises(NotImplementedError):
                c.execute('show version', target = 'standby')
        finally:
            c.disconnect()
            md.stop()

if __name__ == '__main__':
    unittest.main()
