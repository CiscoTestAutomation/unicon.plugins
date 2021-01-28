"""
Unittests for ASA/FP2K plugin

"""

__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import unittest
from unittest.mock import patch

import unicon
from unicon import Connection


@patch.object(unicon.settings.Settings, 'POST_DISCONNECT_WAIT_SEC', 0)
@patch.object(unicon.settings.Settings, 'GRACEFUL_DISCONNECT_WAIT_SEC', 0)
class TestAsaFp2kPlugin(unittest.TestCase):

    def test_connect(self):
        c = Connection(
            hostname='ASA',
            start=['mock_device_cli --os asa --state asa_disable'],
            os='asa',
            platform='fp2k',
            credentials=dict(default=dict(username='cisco', password='cisco'), enable=dict(password='cisco')),
        )
        c.connect()
        self.assertEqual(c.state_machine.current_state, 'disable')
        c.disconnect()

    def test_switchto(self):
        c = Connection(
            hostname='ASA',
            start=['mock_device_cli --os asa --state asa_fp2k_console_disable'],
            os='asa',
            platform='fp2k',
            credentials=dict(default=dict(username='cisco', password='cisco'), enable=dict(password='cisco')),
        )
        c.connect()
        c.switchto('fxos')
        c.switchto(['enable', 'fxos', 'disable'])
        c.switchto('fxos mgmt')
        c.enable()
        c.switchto(['fxos admin', 'fxos root'])
        c.disconnect()

    def test_services(self):
        c = Connection(
            hostname='ASA',
            start=['mock_device_cli --os asa --state asa_fp2k_console_disable'],
            os='asa',
            platform='fp2k',
            credentials=dict(default=dict(username='cisco', password='cisco'), enable=dict(password='cisco')),
        )
        c.connect()
        c.fxos()
        c.sudo()
        c.fxos_mgmt()
        c.disconnect()

    def test_reload(self):
        c = Connection(
            hostname='ASA',
            start=['mock_device_cli --os asa --state asa_fp2k_console_disable'],
            os='asa',
            platform='fp2k',
            credentials=dict(default=dict(username='cisco', password='cisco'), enable=dict(password='cisco')),
        )
        c.connect()
        c.reload()
        c.disconnect()

    def test_rommon(self):
        c = Connection(
            hostname='ASA',
            start=['mock_device_cli --os asa --state asa_fp2k_console_enable_to_rommon'],
            os='asa',
            platform='fp2k',
            credentials=dict(default=dict(username='cisco', password='cisco'), enable=dict(password='cisco')),
        )
        c.connect()
        c.rommon()
        self.assertEqual(c.state_machine.current_state, 'rommon')
        c.enable()
        self.assertEqual(c.state_machine.current_state, 'enable')
        c.disconnect()
