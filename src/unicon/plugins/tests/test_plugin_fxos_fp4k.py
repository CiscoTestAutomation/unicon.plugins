"""
Tests for FXOS/FP4K plugin

"""

__author__ = "dwapstra"

import unittest
from unittest.mock import patch

import unicon
from unicon import Connection
from pyats.topology import loader


unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0


class TestFireOSPlugin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c1 = Connection(
            hostname='Firepower',
            start=['mock_device_cli --os fxos --state fp4k_console'],
            os='fxos',
            platform='fp4k',
            credentials=dict(default=dict(username='admin', password='admin'),
                             enable=dict(password='cisco'),
                             sudo=dict(password='cisco'))
        )
        cls.c2 = Connection(
            hostname='Firepower',
            start=['mock_device_cli --os fxos --state fp4k_ssh_connect'],
            os='fxos',
            platform='fp4k',
            credentials=dict(default=dict(username='admin', password='admin'),
                             enable=dict(password='cisco'),
                             sudo=dict(password='cisco'))
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
        states = ['enable', 'ftd', 'expert', 'sudo', 'fireos', 'enable', 'disable']
        for state in states:
            self.c2.switchto(state)

        for state in states:
            getattr(self.c2, state)()

        self.c2.disconnect()

    def test_reload_console(self):
        self.c1.connect()
        self.c1.reload()
        self.c1.disconnect()

    def test_reload_ssh(self):
        c2 = Connection(
            hostname='Firepower',
            start=['mock_device_cli --os fxos --state fp4k_ssh_fxos'],
            os='fxos',
            platform='fp4k',
            credentials=dict(default=dict(username='admin', password='admin'),
                             enable=dict(password='cisco'),
                             sudo=dict(password='cisco'))
        )
        c2.connect()
        c2.context['console'] = False
        c2.settings.RELOAD_WAIT = 3
        c2.reload()
        c2.disconnect()

    def test_topology(self):
        testbed = """
        devices:
         Firepower:
           os: fxos
           platform: fp4k
           type: fw
           credentials:
            default:
              username: admin
              password: admin
           connections:
             cli:
               command: mock_device_cli --os fxos --state fp4k_console
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
                start=['mock_device_cli --os fxos --state fp4k_asa_{}'.format(initial_state)],
                os='fxos',
                platform='fp4k',
                credentials=dict(default=dict(username='admin', password='admin'),
                                enable=dict(password='cisco')),
            )
            c.connect()
            for state in test_states:
                c.switchto(state)
            c.disconnect()

    def test_rommon(self):
        c = Connection(
            hostname='Firepower',
            start=['mock_device_cli --os fxos --state fp4k_fxos_console_rommon'],
            os='fxos',
            platform='fp4k',
            credentials=dict(default=dict(username='admin', password='admin'),
                             enable=dict(password='cisco')),
        )
        c.connect()
        c.rommon()
        c.fxos()
        c.disconnect()

    def test_disable_enable_username_password(self):
        c = Connection(
            hostname='Firepower',
            start=['mock_device_cli --os fxos --state fp4k_console_module_console_asa_disable_user_pass'],
            os='fxos',
            platform='fp4k',
            connection_timeout=10,
            credentials=dict(default=dict(username='admin', password='admin'),
                             enable=dict(username='admin', password='cisco')),
        )
        c.connect()
        c.enable()
        c.disconnect()

    def test_connect_module_console_username_password(self):
        c = Connection(
            hostname='Firepower',
            start=['mock_device_cli --os fxos --state fp4k_console_fxos_asa_username'],
            os='fxos',
            platform='fp4k',
            # debug=True,
            connection_timeout=10,
            credentials=dict(default=dict(username='admin', password='admin'),
                             enable=dict(username='admin', password='cisco')),
        )
        c.connect()
        c.enable()
        c.disconnect()

    def test_connect_asa_username_password(self):
        c = Connection(
            hostname='Firepower',
            start=['mock_device_cli --os fxos --state fp4k_console_module_telnet_asa'],
            os='fxos',
            platform='fp4k',
            connection_timeout=10,
            credentials=dict(default=dict(username='admin', password='admin'),
                             enable=dict(username='admin', password='cisco')),
        )
        c.connect()
        c.enable()
        c.disconnect()
