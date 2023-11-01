import unittest

import unicon
from unicon import Connection

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2



class TestCheetahAp(unittest.TestCase):

    def test_bash_console(self):
        hostname = 'AP2C57.4152.376C'
        c = Connection(hostname=hostname,
                       start=[f'mock_device_cli --os cheetah --state ap_enable --hostname {hostname}'],
                       os='cheetah',
                       platform='ap',
                       log_buffer=True
                       )
        try:
            c.connect()
            with c.bash_console() as console:
                output = console.execute('pwd')
                self.assertEqual(output, '/tmp')
                self.assertIn(f'{hostname[:6]}:/#', c.spawn.match.match_output)
            self.assertIn('exit', c.spawn.match.match_output)
            self.assertIn(f'{hostname}#', c.spawn.match.match_output)
        finally:
            c.disconnect()


# class TestCheetanApReloadService(unittest.TestCase):
    def test_reload(self):
        dev = Connection(
            hostname = '',
            start = ['mock_device_cli --os cheetah --state ap_enable'],
            os='cheetah',
            platform='ap',
        )
        dev.connect()
        dev.settings.POST_RELOAD_WAIT = 1
        dev.reload(timeout=1800)
        dev.disconnect()

