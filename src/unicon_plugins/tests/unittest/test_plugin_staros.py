"""
Unittests for staros plugin

Uses the mock_device.py script to test the plugin.

"""

__author__ = "dwapstra"


import unittest

from unicon import Connection
from unicon.core.errors import SubCommandFailure


class TestStarosPluginConnect(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='host_name',
                            start=['mock_device_cli --os staros --state staros_connect'],
                            os='staros',
                            username='cisco',
                            tacacs_password='cisco')
        cls.c.connect()

    def test_execute(self):
        r = self.c.execute('')
        self.assertEqual(r, '')

        r = self.c.execute([''])
        self.assertEqual(r, '')

        r = self.c.execute(['']*2)
        self.assertEqual(r, ['', ''])


    def test_configure(self):
        r = self.c.configure('test\ntest123')
        self.assertEqual(r, {'test': '123', 'test123': 'abc'})

    def test_truncation_add_state_pattern(self):
        sm = self.c.state_machine.get_state('config')
        sm.add_state_pattern(r'^(.*?)(newpattern)*#\s?$')
        r = self.c.configure('test_command')
        self.assertEqual(r, 'executing test command')


if __name__ == "__main__":
  unittest.main()

