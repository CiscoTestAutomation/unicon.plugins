"""
Unittests for NXOS/MDS plugin

Uses the unicon.plugins.tests.mock.mock_device_ios script to test NXOS/MDS plugin.

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import re
import unittest

from unicon import Connection
from unicon.core.errors import SubCommandFailure


class TestNxosMdsPluginConnect(unittest.TestCase):

    def test_login_connect(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os nxos_mds --state exec'],
                       os='nxos',
                       platform='mds',
                       credentials=dict(default=dict(username='cisco',
                                        password='cisco')),
                       mit=True)
        c.connect()
        assert c.spawn.match.match_output == 'switch#'


class TestNxosMdsPluginShellexec(unittest.TestCase):

    def test_login_shellexec(self):
        c = Connection(hostname='switch',
                       start=['mock_device_cli --os nxos_mds --state exec'],
                       os='nxos',
                       platform='mds',
                       credentials=dict(default=dict(username='cisco',
                                        password='cisco')),
                       mit=True)
        c.shellexec(['ls'])
        assert c.spawn.match.match_output == 'exit\r\nswitch#'


class TestNxosMdsPluginTie(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='switch',
                           start=['mock_device_cli --os nxos_mds --state exec --hostname switch'],
                           os='nxos',
                           platform='mds',
                           credentials=dict(default=dict(username='cisco', password='cisco')),
                           mit=True)

    def test_execute_tie(self):
        self.c.connect()
        self.c.execute('san-ext-tuner', allow_state_change=True)
        self.c.execute('cmd')
        self.c.enable()

    def test_tie(self):
        self.c.tie('cmd')
        self.c.tie(['cmd', 'cmd'])

    def test_tie_context_mgmr(self):
        with self.c.tie() as tie:
            tie.execute('cmd')
            tie.execute(['cmd', 'cmd'])

    def test_tie_nport(self):
        self.c.tie('nport target disk pWWN 41:00:00:00:00:00:00:14 vsan 20 interface gigabitethernet 1/2 out-interface fc1/14')


if __name__ == "__main__":
    unittest.main()
