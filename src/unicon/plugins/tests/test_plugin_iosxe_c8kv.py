#!/usr/bin/env python3

import os
import re
import unittest
from unittest.mock import Mock

import unicon
from unicon import Connection

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXEC8KVPlugin(unittest.TestCase):
    def test_connect_from_rommon(self):
        """Test connection from c8kv_rommon state (GRUB prompt)"""
        d = Connection(hostname="switch",
                       start=["mock_device_cli --os iosxe --state c8kv_rommon --hostname switch"],
                       os="iosxe",
                       platform="cat8k",
                       log_buffer=True)
        d.connect()
        self.assertEqual(d.state_machine.current_state, 'enable')
        d.disconnect()

    def test_connect_from_exec(self):
        """Test connection from c8kv_exec state"""
        d = Connection(hostname="switch",
                       start=["mock_device_cli --os iosxe --state c8kv_exec --hostname switch"],
                       os="iosxe",
                       platform="c8kv",
                       log_buffer=True)
        d.connect()
        self.assertEqual(d.state_machine.current_state, 'enable')
        d.disconnect()

    def test_grub_prompt_recognition(self):
        """Test that GRUB prompt (grub>) is recognized as rommon state"""
        d = Connection(hostname="switch",
                       start=["mock_device_cli --os iosxe --state c8kv_rommon --hostname switch"],
                       os="iosxe",
                       platform="cat8k",
                       log_buffer=True)
        # Should start in rommon state due to grub> prompt
        d.connect()
        # After boot, should transition to enable state
        self.assertEqual(d.state_machine.current_state, 'enable')
        d.disconnect()


class TestIosXEC8KvPluginReload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='switch',
            start=['mock_device_cli --os iosxe --state c8kv_exec --hostname switch'],
            os='iosxe',
            platform='c8kv',
            credentials=dict(default=dict(
                username='cisco', password='cisco'),
                alt=dict(
                username='admin', password='lab')),
            log_buffer=True,
            )
        cls.c.connect()

    @classmethod
    def tearDownClass(cls):
         cls.c.disconnect()

    def test_reload_with_golden_image(self):
        """Test reload with GOLDEN grub_boot_image"""
        self.c.settings.POST_RELOAD_WAIT = 1
        self.c.reload(grub_boot_image='GOLDEN')
        # Verify device comes back online
        self.assertEqual(self.c.state_machine.current_state, 'enable')

    def test_reload_with_golden_image_phrase(self):
        """Test reload with 'GOLDEN IMAGE' grub_boot_image"""
        self.c.settings.POST_RELOAD_WAIT = 1
        self.c.reload(grub_boot_image='GOLDEN IMAGE')
        # Verify device comes back online
        self.assertEqual(self.c.state_machine.current_state, 'enable')

    def test_reload_without_grub_image(self):
        """Test reload without specifying grub_boot_image (should use default)"""
        self.c.settings.POST_RELOAD_WAIT = 1
        self.c.reload()
        # Verify device comes back online with default boot
        self.assertEqual(self.c.state_machine.current_state, 'enable')

    def test_reload_to_rommon_transition(self):
        """Test that reload can transition through rommon state"""
        # Set autoboot disabled to go through rommon
        self.c.configure('config-register 0x40')
        self.c.settings.POST_RELOAD_WAIT = 1
        # This should go through rommon (grub>) state before reaching enable
        self.c.reload(grub_boot_image='GOLDEN', timeout=10)
        # Should end up in enable state after boot
        self.assertEqual(self.c.state_machine.current_state, 'enable')
        # Restore autoboot
        self.c.configure('config-register 0x2102')

    def test_rommon(self):
        """Test rommon functionality with config register"""
        self.c.rommon(config_register="0x40")


class TestIosXEC8KvPluginStateMachine(unittest.TestCase):
    """Test C8KV-specific state machine behavior"""

    def setUp(self):
        self.c = Connection(
            hostname='switch',
            start=['mock_device_cli --os iosxe --state c8kv_exec --hostname switch'],
            os='iosxe',
            platform='c8kv',
            log_buffer=True
        )
        self.c.connect()

    def tearDown(self):
        self.c.disconnect()

    def test_statemachine_has_rommon_state(self):
        """Test that C8KV statemachine includes rommon state"""
        sm = self.c.state_machine
        self.assertIsNotNone(sm.get_state('rommon'))

    def test_rommon_state_pattern(self):
        """Test that rommon state uses generic pattern for GRUB support"""
        sm = self.c.state_machine
        rommon_state = sm.get_state('rommon')
        # Should use generic patterns that include grub> prompt
        self.assertIsNotNone(rommon_state.pattern)

    def test_rommon_to_disable_path_exists(self):
        """Test that custom rommon->disable path exists"""
        sm = self.c.state_machine
        path = sm.get_path('rommon', 'disable')
        self.assertIsNotNone(path, "No rommon->disable path found")


class TestIosXEC8KvPluginBootStatements(unittest.TestCase):
    """Test C8KV boot statement functionality"""

    def test_boot_context_handling(self):
        """Test that boot statements handle context properly"""
        from unicon.plugins.iosxe.c8kv.statements import boot_from_rommon
        from unittest.mock import Mock, MagicMock

        # Mock objects
        statemachine = Mock()
        spawn = Mock()

        # Test with grub_boot_image specified
        context = {'grub_boot_image': 'GOLDEN'}
        boot_from_rommon(statemachine, spawn, context)

        # Verify escape character was sent
        spawn.send.assert_called_with('\x1b')
        # Verify context was updated with boot timing
        self.assertIn('boot_start_time', context)
        self.assertIn('boot_prompt_count', context)

    def test_boot_without_grub_image(self):
        """Test boot statements without grub_boot_image"""
        from unicon.plugins.iosxe.c8kv.statements import boot_from_rommon
        from unittest.mock import Mock

        statemachine = Mock()
        spawn = Mock()
        context = {}  # No grub_boot_image specified

        boot_from_rommon(statemachine, spawn, context)

        # Should still send escape and update context
        spawn.send.assert_called_with('\x1b')
        self.assertIn('boot_start_time', context)
        self.assertEqual(context['boot_prompt_count'], 1)


if __name__ == "__main__":
    unittest.main()