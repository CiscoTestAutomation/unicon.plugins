"""
Tests for FXOS plugin

"""

__author__ = "dwapstra"

import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from pyats.topology import loader


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestFireOSPlugin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c1 = Connection(
            hostname='Firepower',
            start=['mock_device_cli --os fxos --state fp2k_fxos_console'],
            os='fxos',
            credentials=dict(default=dict(username='admin', password='admin'), enable=dict(password='')),
        )
        cls.c2 = Connection(
            hostname='Firepower',
            start=['mock_device_cli --os fxos --state fp2k_ftd_connect_ssh'],
            os='fxos',
            credentials=dict(default=dict(username='admin', password='admin'), enable=dict(password='')),
        )

    def test_connect_console(self):
        self.c1.connect()
        states = ['enable', 'fxos', 'ftd', 'expert', 'sudo', 'fireos', 'enable', 'disable', 'fxos']
        for state in states:
            self.c1.switchto(state)

        for state in states:
            getattr(self.c1, state)()

        self.c1.disconnect()

    def test_connect_ssh(self):
        self.c2.connect()
        states = ['enable', 'fxos', 'ftd', 'expert', 'sudo', 'fireos', 'enable', 'disable', 'fxos']
        for state in states:
            self.c2.switchto(state)

        for state in states:
            getattr(self.c2, state)()

        self.c2.disconnect()

    def test_reload_console(self):
        self.c1.connect()
        self.c1.settings.POST_RELOAD_WAIT = 1
        self.c1.reload()
        self.c1.disconnect()

    def test_reload_ssh(self):
        self.c2.connect()
        self.c2.context['console'] = False
        self.c2.settings.RELOAD_WAIT = 3
        self.c1.settings.POST_RELOAD_WAIT = 1
        self.c2.reload()
        self.c2.disconnect()

    def test_topology(self):
        testbed = """
        devices:
         Firepower:
           os: fxos
           type: fw
           credentials:
            default:
              username: admin
              password: admin
           connections:
             cli:
               command: mock_device_cli --os fxos --state fp2k_fxos_console
               arguments:
                 console: True
        """
        tb = loader.load(testbed)
        tb.devices.Firepower.connect()
        tb.devices.Firepower.disconnect()

    def test_system_cli_transition(self):
        test_states = ['disable', 'enable', 'config']
        for initial_state in test_states:
            c = Connection(
                hostname='Firepower',
                start=['mock_device_cli --os fxos --state fp2k_ftd_exec_{}'.format(initial_state)],
                os='fxos',
                credentials=dict(default=dict(username='admin', password='admin')),
            )
            c.connect()
            for state in test_states:
                c.switchto(state)
            c.disconnect()

    def test_rommon(self):
        c = Connection(
            hostname='Firepower',
            start=['mock_device_cli --os fxos --state fp2k_fxos_console_rommon'],
            os='fxos',
            credentials=dict(default=dict(username='admin', password='admin'), enable=dict(password='')),
        )
        c.connect()
        c.rommon()
        c.fxos()
        c.disconnect()
