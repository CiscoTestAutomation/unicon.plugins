import unittest

import unicon
from unicon import Connection

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2



class TestCheetahAp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.hostname = 'AP2C57.4152.376C'
        cls.c = Connection(hostname=cls.hostname,
                           start=[f'mock_device_cli --os cheetah --state ap_enable --hostname {cls.hostname}'],
                           os='cheetah',
                           platform='ap',
                           log_buffer=True
                           )
        cls.c.connect()

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()

    def test_bash_console(self):
        with self.c.bash_console() as console:
            output = console.execute('pwd')
            self.assertEqual(output, '/tmp')
            self.assertIn(f'{self.hostname[:6]}:/#', self.c.spawn.match.match_output)
        self.assertIn('exit', self.c.spawn.match.match_output)
        self.assertIn(f'{self.hostname}#', self.c.spawn.match.match_output)

    def test_execute_with_more(self):
        self.c.settings.MORE_CONTINUE = '\r'
        output = self.c.execute('show command with more')
        self.assertEqual(output, 'first\r\n\r\nsecond\r\n\r\nthird')
        self.assertEqual(repr(output), repr('first\r\n\r\nsecond\r\n\r\nthird'))


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
