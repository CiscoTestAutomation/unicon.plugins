__author__ = 'Difu Hu <pyats-support@cisco.com;pyats-support-ext@cisco.com>'

import unittest
from unittest.mock import patch

from unicon import Connection
from unicon.mock.mock_device import MockDevice
from unicon.plugins.sros import service_implementation

patch.TEST_PREFIX = ('test', 'setUp', 'tearDown')


@patch.object(service_implementation, 'KEY_RETURN_ROOT', 'ctrl+z\n')
class TestSrosPlugin(unittest.TestCase):

    def setUp(self):
        self.md = MockDevice(device_os='sros', state='execute')
        self.joined = lambda string: '\n'.join(string.splitlines())
        self.con = Connection(
            os='sros',
            hostname='COTKON04XR2',
            start=['mock_device_cli --os sros --state connect_ssh'],
            credentials={'default': {'username': 'grpc', 'password': 'nokia'}}
        )
        self.con.connect()

    def tearDown(self):
        cmd = 'show router interface coreloop'
        output = self.con.execute(cmd)
        expect = self.md.mock_data['execute']['commands'][cmd]
        self.assertEqual(self.joined(output), self.joined(expect))

    def test_connect(self):
        self.assertIn('A:grpc@COTKON04XR2#', self.con.spawn.match.match_output)

    def test_execute(self):
        cmd = 'show router interface coreloop'
        output = self.con.execute(cmd)
        expect = self.md.mock_data['execute']['commands'][cmd]
        self.assertEqual(self.joined(output), self.joined(expect))

    def test_configure(self):
        cmd = 'router interface coreloop ipv4 primary address 1.1.1.1 prefix-length 32'
        output = self.con.configure('global', cmd)
        expect = self.md.mock_data['configure_global']['commands'][cmd]
        self.assertIn(self.joined(expect), self.joined(output))

    def test_configure_commit_fail(self):
        cmd = 'router interface coreloop ipv4 primary address 2.2.2.2 prefix-length 32'
        output = self.con.configure('private', cmd)
        expect = self.md.mock_data['configure_private']['commands'][cmd]
        commit = self.md.mock_data['configure_private']['commands']['commit']
        self.assertIn(self.joined(expect), self.joined(output))
        self.assertIn(self.joined(commit), self.joined(output))

    def test_classic_execute(self):
        cmd = 'show router interface coreloop'
        output = self.con.classic_execute(cmd)
        expect = self.md.mock_data['classic_execute']['commands'][cmd]
        self.assertEqual(self.joined(output), self.joined(expect))

    def test_classic_configure(self):
        cmd = 'configure router interface coreloop address 111.1.1.1 255.255.255.255'
        output = self.con.classic_configure(cmd)
        expect = self.md.mock_data['classic_execute']['commands'][cmd]['response']
        self.assertIn(self.joined(expect), self.joined(output))


if __name__ == '__main__':
    unittest.main()
