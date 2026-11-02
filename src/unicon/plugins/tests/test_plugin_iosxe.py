"""
Unittests for Generic/IOSXE plugin

Uses the unicon.plugins.tests.mock.mock_device_ios script to test IOSXE plugin.

"""

__author__ = "Myles Dear <mdear@cisco.com>"

import re
import os 
import time
import unittest
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch, Mock, MagicMock
from pyats.topology import loader

import unicon
from unicon.plugins.generic.statements import (
    connection_statement_list,
    generic_statements,
    terminal_position_handler,
)
from unicon.plugins.generic.service_implementation import (
    Reload as GenericReload,
)
from unicon import Connection
from unicon.eal.dialogs import Dialog, Statement
from unicon.eal.utils import ExpectMatch, MatchMode
from unicon.core.errors import (
    ConnectionError as UniconConnectionError,
    StateMachineError,
    SubCommandFailure,
    UniconAuthenticationError,
)
from unicon.plugins.iosxe.ie3k.settings import IosXEIe3kSettings
from unicon.plugins.iosxe.ie9k.settings import IosXEIe9kSettings
from unicon.plugins.iosxe.service_implementation import Reload as IosXEReload
from unicon.plugins.iosxe.patterns import IosXEPatterns
from unicon.plugins.iosxe.service_statements import (
    command_echo_corruption_stmt,
    command_echo_statement_list,
)
from unicon.plugins.iosxe.sdwan.statemachine import (
    SDWANDualRpStateMachine,
    SDWANSingleRpStateMachine,
)
from unicon.plugins.iosxe.statemachine import (
    IosXEDualRpStateMachine,
    IosXESingleRpStateMachine,
)
from unicon.plugins.iosxe.statements import (
    boot_finished_deco,
    boot_from_rommon_statement_list,
    boot_image,
)
from unicon.plugins.tests.mock.mock_device_iosxe import (
    MockDeviceTcpWrapperIOSXE,
)

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXEPatterns(unittest.TestCase):

    def test_enable_prompt_incomplete_command_pattern(self):
        patterns = IosXEPatterns()
        expected = (
            r'(?:\x00|\^@)[\r\n]+.*?'
            + patterns.enable_prompt[6:-1]
            + r'\w+[\w\s-]+$'
        )
        self.assertEqual(patterns.enable_prompt_incomplete_command, expected)
        self.assertTrue(patterns.enable_prompt.startswith(r'^(.*?)'))
        self.assertTrue(patterns.enable_prompt.endswith('$'))

        # Dialog processes multiline console output with DOTALL enabled.
        pattern = re.compile(expected, re.DOTALL)
        for marker in ('^@', '\x00'):
            with self.subTest(marker=repr(marker)):
                wireless = (
                    's' + marker + '\r\n'
                    '% Type "show ?" for a list of subcommands\r\n'
                    'Switch#how wireless cl'
                )
                self.assertRegex(wireless, pattern)
                hyphenated = wireless.replace(
                    'Switch#how wireless cl',
                    'Switch#how wireless running-con')
                self.assertRegex(hyphenated, pattern)
                self.assertRegex(wireless.replace(
                    'Switch#how wireless cl', 'Switch#how running-con'),
                    pattern)
                self.assertNotRegex(hyphenated.replace(
                    'Switch#', 'Switch(config)#'), pattern)
                self.assertNotRegex(
                    wireless.replace('Switch#', 'Switch(config)#'), pattern)
                self.assertNotRegex(
                    wireless.replace('Switch#', 'Switch>'), pattern)
                self.assertNotRegex(
                    wireless.replace('Switch#', 'arbitrary-output#'), pattern)

    def test_incomplete_command_requires_marker_and_pending_input(self):
        pattern = re.compile(
            IosXEPatterns().enable_prompt_incomplete_command, re.DOTALL)
        self.assertNotRegex('s\r\nSwitch#how wireless cl', pattern)
        self.assertNotRegex('s^@\r\nSwitch#', pattern)
        self.assertNotRegex('s^@\r\nSwitch#\r\n', pattern)

    def test_incomplete_command_statement_uses_iosxe_pattern(self):
        self.assertEqual(
            command_echo_corruption_stmt.pattern,
            IosXEPatterns().enable_prompt_incomplete_command)
        self.assertFalse(command_echo_corruption_stmt.loop_continue)
        self.assertEqual(
            command_echo_statement_list, [command_echo_corruption_stmt])


class TestIosXEStatements(unittest.TestCase):

    class RommonDialogSpawn:

        def __init__(self):
            self.timeout = 1
            self.hostname = None
            self.match = ExpectMatch()
            self.log = Mock()

        def read_update_buffer(self, size=None):
            return 'Connection closed by foreign host'

        def match_buffer(self, patterns):
            self.match.match_output = 'Connection closed by foreign host'
            return 0

        def trim_buffer(self):
            pass

        def __str__(self):
            return 'Router'

    def test_boot_finished_decorator_maps_arguments_by_name(self):
        spawn = Mock()
        session = {'booting': True}
        context = {'boot_start_time': object()}
        received = {}

        def callback(spawn, /, context, *, wait=None):
            received.update(spawn=spawn, context=context, wait=wait)

        decorated_callback = boot_finished_deco(callback)
        decorated_callback(
            spawn, session, context, wait=5, unused_argument=True
        )

        self.assertEqual(
            received,
            {'spawn': spawn, 'context': context, 'wait': 5},
        )
        self.assertNotIn('boot_start_time', context)

    def test_boot_finished_decorator_forwards_statement_arguments(self):
        spawn = Mock()
        received = {}

        def callback(spawn, **kwargs):
            received.update(spawn=spawn, kwargs=kwargs)

        boot_finished_deco(callback)(
            spawn, {'booting': True}, {}, wait=5
        )

        self.assertEqual(received, {'spawn': spawn, 'kwargs': {'wait': 5}})

    def test_boot_finished_decorator_propagates_callback_type_error_once(self):
        spawn = Mock()
        callback_calls = []

        def callback(spawn):
            callback_calls.append(spawn)
            raise TypeError('callback failure')

        with self.assertRaisesRegex(TypeError, 'callback failure'):
            boot_finished_deco(callback)(
                spawn, {}, {'boot_start_time': object()}
            )

        self.assertEqual(callback_calls, [spawn])

    def test_boot_from_rommon_dialog_supports_spawn_only_callback(self):
        disconnect_statement = next(
            statement for statement in boot_from_rommon_statement_list
            if statement.pattern ==
            generic_statements.disconnect_error_stmt.pattern
        )
        context = {'boot_start_time': object()}

        with self.assertRaisesRegex(
                Exception, 'received disconnect from router Router'):
            Dialog([disconnect_statement]).process(
                self.RommonDialogSpawn(), timeout=1, context=context
            )

        self.assertNotIn('boot_start_time', context)

    def test_boot_from_rommon_dialog_supports_spawn_context_callback(self):
        connection_refused_statement = next(
            statement for statement in boot_from_rommon_statement_list
            if statement.pattern ==
            generic_statements.connection_refused_stmt.pattern
        )
        spawn = self.RommonDialogSpawn()
        spawn.device = None
        context = {'boot_start_time': object()}

        with self.assertRaisesRegex(
                ConnectionRefusedError,
                'Connection refused to device Router') as cm:
            Dialog([connection_refused_statement]).process(
                spawn, timeout=1, context=context
            )

        self.assertEqual(context, {})
        self.assertIs(cm.exception.spawn, spawn)
        self.assertIs(cm.exception.context, context)

    def test_boot_from_rommon_owns_generic_connection_statements(self):
        iosxe_connection_statements = boot_from_rommon_statement_list[
            -len(connection_statement_list):
        ]

        self.assertEqual(
            len(iosxe_connection_statements),
            len(connection_statement_list),
        )
        for iosxe_statement, generic_statement in zip(
                iosxe_connection_statements, connection_statement_list):
            self.assertIsNot(iosxe_statement, generic_statement)

    def test_boot_image_finds_images_from_multiple_filesystems(self):
        spawn = Mock()
        spawn.settings = SimpleNamespace(
            MAX_BOOT_ATTEMPTS=5,
            FIND_BOOT_IMAGE=True,
            BOOT_FILESYSTEM=['bootflash:', 'flash:'],
            BOOT_FILE_REGEX=r'(\S+\.bin)'
        )
        spawn.expect.side_effect = [
            Mock(match_output='bootflash: cat9k_gold.bin cat9k_prod.bin'),
            Mock(match_output='flash: emergency.bin')
        ]

        context = {}
        session = {}

        boot_image(spawn, context, session)

        self.assertEqual(
            spawn.sendline.call_args_list,
            [
                unittest.mock.call('dir bootflash:'),
                unittest.mock.call('dir flash:'),
                unittest.mock.call('boot bootflash:cat9k_gold.bin')
            ]
        )
        self.assertEqual(
            context['filesystem_images'],
            ['bootflash:cat9k_prod.bin', 'flash:emergency.bin']
        )
        self.assertEqual(context['boot_prompt_count'], 2)

    @patch('unicon.plugins.iosxe.statements._find_boot_images')
    def test_boot_image_skips_emergency_discovery_without_complete_settings(
        self, find_boot_images
    ):
        settings_without_emergency_discovery = (
            {},
            {'EMERGENCY_FILESYSTEMS': []},
            {'EMERGENCY_FILESYSTEMS': ['emgy:']},
        )
        for emergency_settings in settings_without_emergency_discovery:
            with self.subTest(emergency_settings=emergency_settings):
                spawn = Mock()
                spawn.settings = SimpleNamespace(
                    MAX_BOOT_ATTEMPTS=5,
                    FIND_BOOT_IMAGE=True,
                    BOOT_FILESYSTEM=['flash:'],
                    BOOT_FILE_REGEX=r'(\S+\.bin)',
                    **emergency_settings,
                )
                find_boot_images.reset_mock()
                find_boot_images.return_value = ['flash:image.bin']

                boot_image(spawn, {}, {})

                find_boot_images.assert_called_once_with(
                    spawn,
                    ['flash:'],
                    r'(\S+\.bin)',
                )
                spawn.sendline.assert_called_once_with(
                    'boot flash:image.bin')

    def test_boot_image_uses_cached_filesystem_images_fifo_order(self):
        spawn = Mock()
        spawn.settings = SimpleNamespace(
            MAX_BOOT_ATTEMPTS=5,
            FIND_BOOT_IMAGE=True,
            BOOT_FILESYSTEM=['bootflash:', 'flash:'],
            BOOT_FILE_REGEX=r'(\S+\.bin)'
        )
        spawn.expect.side_effect = [
            Mock(match_output='bootflash: cat9k_gold.bin cat9k_prod.bin'),
            Mock(match_output='flash: emergency.bin')
        ]

        context = {}
        session = {}

        # First call builds the filesystem image list and boots first image.
        boot_image(spawn, context, session)

        spawn.sendline.reset_mock()
        spawn.expect.reset_mock()

        # Second call should use cached images in FIFO order without re-running dir.
        boot_image(spawn, context, session)

        spawn.expect.assert_not_called()
        spawn.sendline.assert_called_once_with('boot bootflash:cat9k_prod.bin')
        self.assertEqual(context['filesystem_images'], ['flash:emergency.bin'])
        self.assertEqual(context['boot_prompt_count'], 3)

    def test_boot_image_does_not_rebuild_an_exhausted_queue(self):
        spawn = Mock()
        spawn.settings = SimpleNamespace(
            MAX_BOOT_ATTEMPTS=5,
            FIND_BOOT_IMAGE=True,
            BOOT_FILESYSTEM=['bootflash:'],
            BOOT_FILE_REGEX=r'(\S+\.bin)',
        )
        spawn.expect.return_value = Mock(
            match_output='bootflash: fallback.bin')
        context = {}

        boot_image(spawn, context, {})
        boot_image(spawn, context, {})

        spawn.expect.assert_called_once()
        self.assertEqual(
            spawn.sendline.call_args_list,
            [
                unittest.mock.call('dir bootflash:'),
                unittest.mock.call('boot bootflash:fallback.bin'),
                unittest.mock.call('boot'),
            ],
        )

    def test_boot_image_honors_max_boot_attempts(self):
        spawn = Mock()
        spawn.settings = SimpleNamespace(
            MAX_BOOT_ATTEMPTS=3,
            FIND_BOOT_IMAGE=False,
        )
        context = {}

        for _ in range(3):
            boot_image(spawn, context, {})
        with self.assertRaisesRegex(Exception, 'Too many failed boot attempts'):
            boot_image(spawn, context, {})

        self.assertEqual(
            spawn.sendline.call_args_list,
            [unittest.mock.call('boot')] * 3,
        )

    def test_boot_image_orders_images_with_boot_file_regex_list(self):
        spawn = Mock()
        spawn.settings = SimpleNamespace(
            MAX_BOOT_ATTEMPTS=5,
            FIND_BOOT_IMAGE=True,
            BOOT_FILESYSTEM=['flash:'],
            BOOT_FILE_REGEX=[
                r'(\S+\.SSA\.bin)',
                r'(\S+\.SPA\.bin)',
                r'(\S+\.bin)',
            ],
        )
        spawn.expect.return_value = Mock(
            match_output='flash: ie35xx.BLD_x.SPA.bin ie35xx.BLD_y.SSA.bin ie35xx.BLD_z.bin'
        )

        context = {}
        session = {}

        boot_image(spawn, context, session)

        self.assertEqual(
            spawn.sendline.call_args_list,
            [
                unittest.mock.call('dir flash:'),
                unittest.mock.call('boot flash:ie35xx.BLD_y.SSA.bin'),
            ],
        )
        self.assertEqual(
            context['filesystem_images'],
            ['flash:ie35xx.BLD_x.SPA.bin', 'flash:ie35xx.BLD_z.bin'],
        )

    def test_boot_image_deduplicates_images_from_boot_file_regex_list(self):
        spawn = Mock()
        spawn.settings = SimpleNamespace(
            MAX_BOOT_ATTEMPTS=5,
            FIND_BOOT_IMAGE=True,
            BOOT_FILESYSTEM=['flash:'],
            BOOT_FILE_REGEX=[
                r'(\S+\.SSA\.bin)',
                r'(\S+\.bin)',
            ],
        )
        spawn.expect.return_value = Mock(
            match_output='flash: image1.SSA.bin image2.bin'
        )

        context = {}
        session = {}

        boot_image(spawn, context, session)

        self.assertEqual(
            spawn.sendline.call_args_list,
            [
                unittest.mock.call('dir flash:'),
                unittest.mock.call('boot flash:image1.SSA.bin'),
            ],
        )
        self.assertEqual(context['filesystem_images'], ['flash:image2.bin'])

    def test_boot_image_orders_filesystem_images_by_boot_file_regex_priority(self):
        spawn = Mock()
        spawn.settings = SimpleNamespace(
            MAX_BOOT_ATTEMPTS=5,
            FIND_BOOT_IMAGE=True,
            BOOT_FILESYSTEM=['bootflash:', 'flash:'],
            BOOT_FILE_REGEX=[
                r'(\S+\.SSA\.bin)',
                r'(\S+\.SPA\.bin)',
                r'(\S+\.bin)',
            ],
        )
        spawn.expect.side_effect = [
            Mock(match_output='bootflash: bootflash_spa.SPA.bin bootflash_other.bin'),
            Mock(match_output='flash: flash_ssa.SSA.bin flash_other.bin'),
        ]

        context = {}
        session = {}

        boot_image(spawn, context, session)

        self.assertEqual(
            spawn.sendline.call_args_list,
            [
                unittest.mock.call('dir bootflash:'),
                unittest.mock.call('dir flash:'),
                unittest.mock.call('boot flash:flash_ssa.SSA.bin'),
            ],
        )
        self.assertEqual(
            context['filesystem_images'],
            [
                'bootflash:bootflash_spa.SPA.bin',
                'bootflash:bootflash_other.bin',
                'flash:flash_other.bin',
            ],
        )

    def test_boot_image_orders_filesystem_images_by_boot_file_regex_priority(self):
        spawn = Mock()
        spawn.settings = SimpleNamespace(
            MAX_BOOT_ATTEMPTS=5,
            FIND_BOOT_IMAGE=True,
            BOOT_FILESYSTEM=['bootflash:', 'flash:'],
            BOOT_FILE_REGEX=[
                r'(\S+\.SSA\.bin)',
                r'(\S+\.SPA\.bin)',
                r'(\S+\.bin)',
            ],
        )
        spawn.expect.side_effect = [
            Mock(match_output='bootflash: bootflash_spa.SPA.bin bootflash_other.bin'),
            Mock(match_output='flash: flash_ssa.SSA.bin flash_other.bin'),
        ]

        context = {}
        session = {}

        boot_image(spawn, context, session)

        self.assertEqual(
            spawn.sendline.call_args_list,
            [
                unittest.mock.call('dir bootflash:'),
                unittest.mock.call('dir flash:'),
                unittest.mock.call('boot flash:flash_ssa.SSA.bin'),
            ],
        )
        self.assertEqual(
            context['filesystem_images'],
            [
                'bootflash:bootflash_spa.SPA.bin',
                'bootflash:bootflash_other.bin',
                'flash:flash_other.bin',
            ],
        )

    def test_boot_image_passes_rommon_dir_timeout_to_expect(self):
        spawn = Mock()
        spawn.settings = SimpleNamespace(
            MAX_BOOT_ATTEMPTS=5,
            FIND_BOOT_IMAGE=True,
            BOOT_FILESYSTEM=['bootflash:'],
            BOOT_FILE_REGEX=r'(\S+\.bin)',
            ROMMON_DIR_TIMEOUT=120,
        )
        spawn.expect.return_value = Mock(
            match_output='bootflash: cat9k_gold.bin'
        )

        boot_image(spawn, {}, {})

        spawn.expect.assert_called_once_with(
            unittest.mock.ANY, timeout=120
        )

    def test_boot_image_prioritizes_emergency_filesystems(self):
        spawn = Mock()
        spawn.settings = SimpleNamespace(
            MAX_BOOT_ATTEMPTS=5,
            FIND_BOOT_IMAGE=True,
            EMERGENCY_FILESYSTEMS=['emgy:', 'emgy0:'],
            EMERGENCY_IMAGE_PATTERN=r'(\d+)\s+(\S+\.bin)',
            BOOT_FILESYSTEM=['flash:', 'sdflash:'],
            BOOT_FILE_REGEX=[
                r'(\S+\.SSA\.bin)',
                r'(\S+\.SPA\.bin)',
                r'(\S+\.bin)',
            ],
        )
        spawn.expect.side_effect = [
            Mock(match_output='emgy: 1234 emergency.bin'),
            Mock(match_output='emgy0: 2345 alternate.SPA.bin'),
            Mock(match_output='flash: flash.SPA.bin flash.SSA.bin'),
            Mock(match_output='sdflash: sdflash.SSA.bin fallback.bin'),
        ]

        context = {'recovery_images': ['flash:golden_image.bin']}
        boot_image(spawn, context, {})

        self.assertEqual(
            spawn.sendline.call_args_list,
            [
                unittest.mock.call('dir emgy:'),
                unittest.mock.call('dir emgy0:'),
                unittest.mock.call('dir flash:'),
                unittest.mock.call('dir sdflash:'),
                unittest.mock.call('boot emgy:emergency.bin'),
            ],
        )
        self.assertEqual(
            context['filesystem_images'],
            [
                'emgy0:alternate.SPA.bin',
                'flash:golden_image.bin',
                'flash:flash.SSA.bin',
                'sdflash:sdflash.SSA.bin',
                'flash:flash.SPA.bin',
                'sdflash:fallback.bin',
            ],
        )

    def test_boot_image_prioritizes_recovery_before_normal_filesystems(self):
        spawn = Mock()
        spawn.settings = SimpleNamespace(
            MAX_BOOT_ATTEMPTS=5,
            FIND_BOOT_IMAGE=True,
            BOOT_FILESYSTEM=['flash:', 'sdflash:'],
            BOOT_FILE_REGEX=[
                r'(\S+\.SSA\.bin)',
                r'(\S+\.SPA\.bin)',
                r'(\S+\.bin)',
            ],
        )
        spawn.expect.side_effect = [
            Mock(match_output='flash: fallback.SPA.bin'),
            Mock(match_output=(
                'sdflash: preferred.SSA.bin golden_image.bin')),
        ]
        context = {
            'recovery_images': ['sdflash:golden_image.bin'],
        }

        boot_image(spawn, context, {})

        spawn.sendline.assert_called_with(
            'boot sdflash:golden_image.bin')
        self.assertEqual(
            context['filesystem_images'],
            ['sdflash:preferred.SSA.bin', 'flash:fallback.SPA.bin'],
        )

    def test_boot_image_uses_recovery_when_discovery_is_disabled(self):
        spawn = Mock()
        spawn.settings = SimpleNamespace(
            MAX_BOOT_ATTEMPTS=3,
            FIND_BOOT_IMAGE=False,
        )
        context = {'recovery_images': 'bootflash:golden_image.bin'}

        boot_image(spawn, context, {})

        spawn.expect.assert_not_called()
        spawn.sendline.assert_called_once_with(
            'boot bootflash:golden_image.bin')

    def test_boot_image_normalizes_mapping_recovery_image(self):
        spawn = Mock()
        spawn.settings = SimpleNamespace(
            MAX_BOOT_ATTEMPTS=3,
            FIND_BOOT_IMAGE=False,
        )
        context = {
            'recovery_images': {
                'system': 'flash:golden_image.bin',
            },
        }

        boot_image(spawn, context, {})

        spawn.expect.assert_not_called()
        spawn.sendline.assert_called_once_with(
            'boot flash:golden_image.bin')

    def test_reload_publishes_and_cleans_recovery_image_context(self):
        service = object.__new__(IosXEReload)
        service.context = {}
        service.connection = SimpleNamespace(
            settings=SimpleNamespace(USE_RECOVERY_IMAGE_ON_RELOAD=True),
            device=SimpleNamespace(clean={
                'device_recovery': {
                    'golden_image': ['bootflash:golden_image.bin'],
                },
            }),
        )
        service.get_sm = Mock(
            return_value=SimpleNamespace(current_state='enable'))
        captured_context = {}

        def fail_reload(*args, **kwargs):
            captured_context.update(service.context)
            raise RuntimeError('reload failed')

        with patch.object(
                GenericReload, 'call_service', side_effect=fail_reload):
            with self.assertRaisesRegex(RuntimeError, 'reload failed'):
                service.call_service()

        self.assertEqual(
            captured_context['recovery_images'],
            ['bootflash:golden_image.bin'],
        )
        for context_key in (
            'image_to_boot',
            'grub_boot_image',
            'recovery_images',
            'filesystem_images',
            'boot_image_queue_initialized',
            'boot_prompt_count',
        ):
            self.assertNotIn(context_key, service.context)

    def test_reload_recovery_image_is_disabled_for_other_platforms(self):
        service = object.__new__(IosXEReload)
        service.context = {}
        service.connection = SimpleNamespace(
            settings=SimpleNamespace(),
            device=SimpleNamespace(clean={
                'device_recovery': {
                    'golden_image': ['bootflash:golden_image.bin'],
                },
            }),
        )
        service.get_sm = Mock(
            return_value=SimpleNamespace(current_state='enable'))
        captured_context = {}

        def fail_reload(*args, **kwargs):
            captured_context.update(service.context)
            raise RuntimeError('reload failed')

        with patch.object(
                GenericReload, 'call_service', side_effect=fail_reload):
            with self.assertRaisesRegex(RuntimeError, 'reload failed'):
                service.call_service()

        self.assertEqual(captured_context['recovery_images'], [])

    def test_reload_cleans_explicit_boot_command_context(self):
        service = object.__new__(IosXEReload)
        service.context = {}
        service.connection = SimpleNamespace(
            settings=SimpleNamespace(USE_RECOVERY_IMAGE_ON_RELOAD=True),
            device=SimpleNamespace(clean={}),
        )
        service.get_sm = Mock(
            return_value=SimpleNamespace(current_state='rommon'))
        captured_contexts = []

        def capture_reload_context(*args, **kwargs):
            captured_contexts.append(service.context.copy())

        with patch.object(
                GenericReload, 'call_service',
                side_effect=capture_reload_context):
            service.call_service(
                reload_command='boot flash:explicit.bin')
            service.call_service()

        self.assertEqual(
            captured_contexts[0]['boot_cmd'],
            'boot flash:explicit.bin',
        )
        self.assertNotIn('boot_cmd', captured_contexts[1])
        self.assertNotIn('boot_cmd', service.context)

    def test_boot_image_falls_back_when_no_emergency_image_is_found(self):
        spawn = Mock()
        spawn.settings = SimpleNamespace(
            MAX_BOOT_ATTEMPTS=5,
            FIND_BOOT_IMAGE=True,
            EMERGENCY_FILESYSTEMS=['emgy:', 'emgy0:'],
            EMERGENCY_IMAGE_PATTERN=r'(\d+)\s+(\S+\.bin)',
            BOOT_FILESYSTEM=['flash:', 'sdflash:'],
            BOOT_FILE_REGEX=[
                r'(\S+\.SSA\.bin)',
                r'(\S+\.SPA\.bin)',
                r'(\S+\.bin)',
            ],
        )
        spawn.expect.side_effect = [
            Mock(match_output='emgy: unknown filesystem'),
            Mock(match_output='emgy0: directory is empty'),
            Mock(match_output='flash: fallback.SPA.bin'),
            Mock(match_output='sdflash: preferred.SSA.bin'),
        ]

        context = {}
        boot_image(spawn, context, {})

        spawn.sendline.assert_called_with('boot sdflash:preferred.SSA.bin')
        self.assertEqual(
            context['filesystem_images'],
            ['flash:fallback.SPA.bin'],
        )

    def test_ie_settings_define_emergency_and_ranked_boot_images(self):
        for settings in (IosXEIe3kSettings(), IosXEIe9kSettings()):
            with self.subTest(settings=type(settings).__name__):
                self.assertEqual(
                    settings.EMERGENCY_FILESYSTEMS,
                    ['emgy:', 'emgy0:'],
                )
                self.assertEqual(
                    settings.EMERGENCY_IMAGE_PATTERN,
                    r'(\d+)\s+(\S+\.bin)',
                )
                self.assertEqual(
                    settings.BOOT_FILE_REGEX,
                    [
                        r'(\S+\.SSA\.bin)',
                        r'(\S+\.SPA\.bin)',
                        r'(\S+\.bin)',
                    ],
                )


class TestIosXEStateMachine(unittest.TestCase):

    def assert_config_to_enable_prompt_handler(self, state_machine_class):
        state_machine = state_machine_class()
        dialog = state_machine.get_path('config', 'enable').dialog
        prompt_statements = [
            statement for statement in dialog.statements
            if statement.pattern == IosXEPatterns().confirm_uncommited_changes
        ]

        self.assertEqual(len(prompt_statements), 1)
        statement = prompt_statements[0]
        self.assertEqual(statement.action.__name__, 'sendline')
        self.assertEqual(statement.args, {'key': 'no'})
        self.assertTrue(statement.loop_continue)

    def test_generic_config_to_enable_prompt_handler(self):
        for state_machine_class in (
                IosXESingleRpStateMachine, IosXEDualRpStateMachine):
            with self.subTest(state_machine=state_machine_class.__name__):
                self.assert_config_to_enable_prompt_handler(
                    state_machine_class)

    def test_sdwan_config_to_enable_prompt_handler_is_not_duplicated(self):
        for state_machine_class in (
                SDWANSingleRpStateMachine, SDWANDualRpStateMachine):
            with self.subTest(state_machine=state_machine_class.__name__):
                self.assert_config_to_enable_prompt_handler(
                    state_machine_class)


class TestIosXEPluginConnect(unittest.TestCase):

    def test_asr_login_connect(self):
        c = Connection(hostname='Router',
                start=['mock_device_cli --os iosxe --state asr_login --hostname Router'],
                os='iosxe',
                credentials=dict(default=dict(username='cisco', password='cisco')),
                log_buffer=True)
        try:
            c.connect()
            self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')
        finally:
            c.disconnect()

    def test_isr_controller_mode_connect(self):
        testbed = '''
            devices:
                Router:
                    type: router
                    os: iosxe
                    platform: isr
                    credentials:
                        default:
                            username: cisco
                            password: cisco
                    connections:
                        defaults:
                            class: 'unicon.Unicon'
                        cli:
                            command: mock_device_cli --os iosxe --state isr_exec_1 --hostname Router
        '''
        t = loader.load(testbed)
        d = t.devices.Router
        try:
            d.connect()
        finally:
            d.disconnect()
        self.assertEqual(d.os, 'iosxe')
        self.assertEqual(d.version, '17.14')
        self.assertEqual(d.platform, 'sdwan')
        self.assertEqual(d.model, 'isr4200')
        self.assertEqual(d.pid, 'ISR4221/K9')


    def test_isr_controller_mode_connect(self):
        testbed = '''
            devices:
                Router:
                    type: router
                    os: iosxe
                    platform: isr
                    credentials:
                        default:
                            username: cisco
                            password: cisco
                    connections:
                        defaults:
                            class: 'unicon.Unicon'
                        cli:
                            command: mock_device_cli --os iosxe --state isr_exec_1 --hostname Router
        '''
        t = loader.load(testbed)
        d = t.devices.Router
        try:
            d.connect()
        finally:
            d.disconnect()
        self.assertEqual(d.os, 'iosxe')
        self.assertEqual(d.version, '17.14')
        self.assertEqual(d.platform, 'sdwan')
        self.assertEqual(d.model, 'isr4200')
        self.assertEqual(d.pid, 'ISR4221/K9')


    def test_isr_login_connect(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state isr_login --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        try:
            c.connect()
            self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')
        finally:
            c.disconnect()

    def test_edison_login_connect(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state cat3k_login --hostname Router'],
                       os='iosxe',
                       platform='cat3k',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        try:
            c.connect()
            self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')
        finally:
            c.disconnect()

    def test_edison_login_connect_password_ok(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state cat3k_login --hostname Router'],
                       os='iosxe',
                       platform='cat3k',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        try:
            c.connect()
            self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')
        finally:
            c.disconnect()

    def test_general_login_connect(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_login --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        try:
            c.connect()
            self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')
        finally:
            c.disconnect()

    def test_press_return_rechecks_for_login_prompt(self):
        c = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxe '
                   '--state press_return_then_login --hostname Router'],
            os='iosxe',
            platform='cat8k',
            credentials=dict(
                default=dict(username='cisco', password='cisco')),
            connection_timeout=5,
            log_buffer=True,
            mit=True,
        )
        try:
            c.connect()
            self.assertEqual(c.state_machine.current_state, 'enable')
            self.assertNotIn(
                'BLANK RETURN RECEIVED AT USERNAME', c.log_buffer)
            self.assertLess(
                c.log_buffer.index('Username: cisco'),
                c.log_buffer.index('Password: cisco'),
            )
        finally:
            c.disconnect()

    def test_press_return_without_login_still_sends_return(self):
        c = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxe '
                   '--state press_return_only --hostname Router'],
            os='iosxe',
            credentials=dict(
                default=dict(username='cisco', password='cisco')),
            connection_timeout=5,
            log_buffer=True,
            mit=True,
        )
        try:
            c.connect()
            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()

    def test_press_return_matched_retry_is_bounded(self):
        self.assertEqual(
            generic_statements.press_return_stmt.matched_retries, 1)
        self.assertEqual(
            generic_statements.press_return_stmt.matched_retry_sleep, 1)

    def test_general_login_connect_syslog(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state connect_syslog --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        try:
            c.connect()
            self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')
        finally:
            c.disconnect()

    def test_general_configure(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_login --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        try:
            c.connect()
        finally:
            c.disconnect()

        cmd = ['crypto key generate rsa general-keys modulus 2048 label ca',
               'crypto pki server ca', 'grant auto', 'hash sha256', 'lifetime ca-certificate 3650',
               'lifetime certificate 3650', 'database archive pkcs12 password 0 cisco123', 'no shutdown']
        c.configure(cmd, timeout=60, error_pattern=[], service_dialogue=None)
        self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')

    def test_configure_rsa_key_modulus_prompt_auto_answered(self):
        # The default applies when the caller does not provide a reply.
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe '
                              '--state general_login --hostname Router'],
                       os='iosxe',
                       credentials=dict(
                           default=dict(username='cisco', password='cisco')))
        try:
            c.connect()
            c.configure(
                'crypto key generate rsa general-keys '
                'label 9800-keys exportable', timeout=60)
            self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')
        finally:
            c.disconnect()

    def test_configure_rsa_key_modulus_prompt_caller_override(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe '
                              '--state general_login --hostname Router'],
                       os='iosxe',
                       credentials=dict(
                           default=dict(username='cisco', password='cisco')))
        reply = Dialog([
            Statement(pattern=r'^.*How many bits in the modulus.*:\s*$',
                      action='sendline(3072)',
                      loop_continue=True,
                      continue_timer=False)
        ])
        try:
            c.connect()
            output = c.configure(
                'crypto key generate rsa general-keys '
                'label 9800-keys exportable', reply=reply, timeout=60)
            self.assertIn(
                'How many bits in the modulus [1024]: 3072', output)
            self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')
        finally:
            c.disconnect()

    def test_general_config_ca_profile(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_login --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')))

        try:
            c.connect()
            c.configure("crypto pki profile enrollment test", timeout=60)
            self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')
        finally:
            c.disconnect()

    def test_general_config_ca_cert_map(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_config_certificate_map --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')))

        try:
            c.connect()
            self.assertEqual(c.state_machine.current_state, 'enable')
        finally:
            c.disconnect()

    def test_gkm_local_server(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_login --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        try:
            c.connect()
            cmd = [
                "crypto gkm group g1",
                "identity number 101",
                "server local",
                "end",
                "end"
            ]
            c.configure(cmd, timeout=60)
            self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')
        finally:
            c.disconnect()

    def test_configure_nat_scale_are_you_sure_yes(self):
        """Test that 'Are you sure you want to continue? [yes]:' prompt is handled."""
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_login --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        try:
            c.connect()
            c.configure('nat scale', timeout=60)
            self.assertEqual(c.spawn.match.match_output, 'end\r\nRouter#')
        finally:
            c.disconnect()

    def test_login_console_server_sendline_after(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='ts_login')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            settings=dict(SENDLINE_AFTER_CRED='ts'),
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             ts=dict(username='ts_user', password='ts_pw')),
            login_creds=['ts', 'default'],
            connection_timeout=10
        )
        try:
            c.connect()
        finally:
            c.disconnect()
            md.stop()

    def test_login_console_server_post_cred_action(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='ts_login')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            credentials=dict(default=dict(username='cisco', password='cisco'),
                             ts=dict(username='ts_user', password='ts_pw')),
            login_creds=['ts', 'default'],
            cred_action=dict(ts=dict(post='sendline()')),
            connection_timeout=10
        )
        try:
            c.connect()
        finally:
            c.disconnect()
            md.stop()

    def test_connect_learn_os_version(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='ewc_enable', hostname='EWC')
        md.start()

        testbed = """
        devices:
          EWC:
            os: iosxe
            type: cat9k
            credentials:
                default:
                    username: admin
                    password: cisco
                set1:
                    username: cisco
                    password: cisco
            connections:
              defaults:
                class: unicon.Unicon
                fallback_credentials:
                    - set1
              a:
                protocol: telnet
                ip: 127.0.0.1
                port: {}
        """.format(md.ports[0])

        tb = loader.load(testbed)
        device = tb.devices.EWC
        try:
            with patch.dict(os.environ):
                os.environ.pop('LEARN_OS_VERSION', None)
                device.connect(learn_hostname=True)
                self.assertEqual(device.version, '17.06.01.0.129467')
                self.assertEqual(device.state_machine.current_state, 'enable')
        finally:
            device.disconnect()
            md.stop()

    def test_operating_mode_check(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_enable_no_operating_mode --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')))
        try:
            c.connect()
        finally:
            c.disconnect()

    def test_unlicensed_prompt(self):
        c = Connection(hostname='UUT',
                       start=['mock_device_cli --os iosxe --state unlicensed_prompt --hostname UUT'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       mit=True)
        try:
            c.connect()
            self.assertEqual(c.spawn.match.last_match.group(2), '(unlicensed)')
        finally:
            c.disconnect()

    def test_connect_recovers_from_pnp_timeout_after_prompt(self):
        md = MockDeviceTcpWrapperIOSXE(
            port=0,
            state='pnp_timeout_after_prompt',
            mock_data_dir=os.path.join(
                os.path.dirname(__file__), 'mock_data', 'iosxe'
            ),
        )
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            platform='sdwan',
            mit=True,
            log_buffer=True,
            connection_timeout=3,
            settings=dict(
                POST_DISCONNECT_WAIT_SEC=0,
                GRACEFUL_DISCONNECT_WAIT_SEC=0.2,
                SYSLOG_WAIT=0,
            ),
        )
        try:
            c.connect()
            self.assertEqual(c.state_machine.current_state, 'enable')
            self.assertIn('PnP HTTP timed out', c.log_buffer)
        finally:
            c.disconnect()
            md.stop()


class TestIosXEPluginExecute(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='switch',
                           start=['mock_device_cli --os iosxe --state isr_exec'],
                           os='iosxe',
                           credentials=dict(default=dict(username='cisco', password='cisco')),
                           log_buffer=True
                           )
        cls.c.connect()

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()

    def test_execute_error_pattern(self):
      for cmd in ['not a real command', 'badcommand']:
        with self.assertRaises(SubCommandFailure) as err:
            r = self.c.execute(cmd)

    def test_execute_error_pattern_negative(self):
        r = self.c.execute('not a real command partial')

    def test_execute_stmt_list(self):
      for cmd in ['install remove inactive']:
        r = self.c.execute(cmd)

    def test_execute_with_msgs(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='enable_with_msgs')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            credentials=dict(default=dict(username='cisco', password='cisco')),
            mit=True
        )
        try:
            c.connect()
            c.execute('msg')
        finally:
            c.disconnect()
            md.stop()


class TestIosXECommandEchoRecoveryIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # TERM=dumb uses line input and does not interpret editing keys.
        terminal = patch.dict(os.environ, {'TERM': 'vt100'})
        terminal.start()
        cls.addClassCleanup(terminal.stop)
        cls.device = Connection(
            hostname='Router',
            start=[
                'mock_device_cli --os iosxe --state general_enable '
                '--hostname Router'
            ],
            os='iosxe',
            credentials={
                'default': {
                    'username': 'cisco',
                    'password': 'cisco',
                },
            },
            mit=True,
            log_buffer=True,
        )
        cls.device.connect()

    @classmethod
    def tearDownClass(cls):
        cls.device.disconnect()

    @contextmanager
    def inject_corrupt_echo_once(self, target_command):
        """Inject a rendered NUL once per target command on the PTY."""
        original_sendline = self.device.spawn.sendline
        calls = []
        targets = ([target_command] if isinstance(target_command, str)
                   else target_command)
        injected = set()

        def sendline(command=None):
            calls.append(command)
            if command in targets and command not in injected:
                injected.add(command)
                self.device.spawn.send(command[:1])
                self.device.spawn.send('^@')
                return self.device.spawn.send(
                    '{}\r'.format(command[1:])
                )
            return original_sendline(command)

        self.device.spawn.sendline = sendline
        try:
            yield calls
        finally:
            self.device.spawn.sendline = original_sendline

    def test_terminal_recovery_and_single_retry(self):
        command = 'show clock'
        log_start = len(self.device.log_buffer)

        with patch.object(
                self.device.spawn, 'send',
                wraps=self.device.spawn.send) as send:
            with self.inject_corrupt_echo_once(command) as calls:
                output = self.device.execute(command, timeout=5)

        output_log = self.device.log_buffer[log_start:]
        self.assertIn('UTC', output)
        self.assertEqual(calls, [command, command])
        self.assertIn('s^@how clock', output_log)
        self.assertIn("% Invalid command 's^@how clock'", output_log)
        self.assertEqual(
            output_log.count('Command echo corruption detected'),
            1,
        )
        self.assertEqual(
            [args.args[0] for args in send.call_args_list
             if args.args[0] in ('\x01', '\x0b')],
            ['\x01', '\x0b'],
        )

    def test_terminal_retry_failure_is_not_retried(self):
        command = 'show command-echo failure'
        log_start = len(self.device.log_buffer)

        with self.inject_corrupt_echo_once(command) as calls:
            with self.assertRaises(SubCommandFailure):
                self.device.execute(command, timeout=5)

        output_log = self.device.log_buffer[log_start:]
        self.assertEqual(calls, [command, command])
        self.assertIn('s^@how command-echo failure', output_log)
        self.assertIn(
            "% Invalid command 'show command-echo failure'",
            output_log,
        )
        self.assertEqual(
            output_log.count('Command echo corruption detected'),
            1,
        )

    def test_configure_terminal_recovery_and_single_retry(self):
        command = 'no logging console'
        log_start = len(self.device.log_buffer)
        with patch.object(
                self.device.spawn, 'send',
                wraps=self.device.spawn.send) as send:
            with self.inject_corrupt_echo_once(command) as calls:
                output = self.device.configure(command, timeout=5, bulk=False)
        self.assertEqual(calls.count(command), 2)
        self.assertIn(command, output)
        self.assertIn('n^@o logging console',
                      self.device.log_buffer[log_start:])
        self.assertEqual(
            [args.args[0] for args in send.call_args_list
             if args.args[0] in ('\x01', '\x0b')],
            ['\x01', '\x0b'],
        )

    def test_configure_terminal_retry_failure_is_not_retried(self):
        command = 'command-echo failure'
        log_start = len(self.device.log_buffer)
        with self.inject_corrupt_echo_once(command) as calls:
            with self.assertRaises(SubCommandFailure):
                self.device.configure(command, timeout=5, bulk=False)
        self.assertEqual(calls.count(command), 2)
        self.assertIn("% Invalid command 'command-echo failure'",
                      self.device.log_buffer[log_start:])

    def test_configure_recovers_each_command_independently(self):
        commands = ['no logging console', 'service internal']
        with self.inject_corrupt_echo_once(commands) as calls:
            self.device.configure(commands, timeout=5, bulk=False)
        for command in commands:
            self.assertEqual(calls.count(command), 2)

    def test_execute_recovers_each_command_independently(self):
        commands = ['show clock', 'show version']
        with self.inject_corrupt_echo_once(commands) as calls:
            output = self.device.execute(commands, timeout=5)
        self.assertIn('UTC', output['show clock'])
        self.assertIn('Cisco', output['show version'])
        for command in commands:
            self.assertEqual(calls.count(command), 2)

    def test_bulk_configure_does_not_recover_echo(self):
        commands = ['no logging console', 'service internal']
        chunk = '\n'.join(commands + [
            self.device.settings.BULK_CONFIG_END_INDICATOR])
        with patch.object(
                self.device.spawn, 'send',
                wraps=self.device.spawn.send) as send:
            with self.inject_corrupt_echo_once(chunk) as calls:
                with self.assertRaises(SubCommandFailure):
                    self.device.configure(
                        commands, timeout=5, bulk=True, bulk_chunk_lines=0)
        self.assertEqual(calls.count(chunk), 1)
        self.assertFalse(any(
            args.args[0] in ('\x01', '\x0b')
            for args in send.call_args_list))

    def test_ordinary_execute_and_configure_are_single_attempt(self):
        with patch.object(
                self.device.spawn, 'sendline',
                wraps=self.device.spawn.sendline) as sendline:
            self.device.execute('show clock', timeout=5)
            self.device.configure('no logging console', timeout=5, bulk=False)
        commands = [args.args[0] for args in sendline.call_args_list]
        self.assertEqual(commands.count('show clock'), 1)
        self.assertEqual(commands.count('no logging console'), 1)


class TestIosXEWirelessIncompleteCommand(unittest.TestCase):

    def test_execute_incomplete_command(self):
        # PR #676's wireless reproduction leaves input after the enable
        # prompt. Put the corrupt echo first, as it is in the device log.
        terminal = patch.dict(os.environ, {'TERM': 'vt100'})
        terminal.start()
        self.addCleanup(terminal.stop)
        device = Connection(
            hostname='Switch',
            start=['mock_device_cli --os iosxe --state general_enable'],
            os='iosxe',
            log_buffer=True,
            mit=True,
        )
        device.connect()
        command = 'show wireless client incomplete'
        original_sendline = device.spawn.sendline
        commands = []
        injected = False

        def sendline(value=None):
            nonlocal injected
            commands.append(value)
            if value == command and not injected:
                injected = True
                return original_sendline('s^@')
            return original_sendline(value)

        try:
            device.spawn.sendline = sendline
            with patch.object(
                    device.spawn, 'send', wraps=device.spawn.send) as send:
                output = device.execute(command, timeout=5)
            self.assertIn('Number of Excluded Clients: 0', output)
            self.assertEqual(commands, [command, command])
            self.assertIn('s^@', device.log_buffer)
            self.assertIn('% Type "show ?" for a list of subcommands',
                          device.log_buffer)
            self.assertIn('Switch#how wireless running-con', device.log_buffer)
            self.assertEqual(
                [args.args[0] for args in send.call_args_list
                 if args.args[0] in ('\x01', '\x0b')],
                ['\x01', '\x0b'],
            )
        finally:
            device.spawn.sendline = original_sendline
            device.disconnect()


class TestIosXEPluginDisableEnable(unittest.TestCase):

    def test_disable_enable(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state isr_exec --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )

        r = c.disable()
        self.assertEqual(c.spawn.match.match_output, 'disable\r\nRouter>')

        r = c.enable()
        self.assertEqual(c.spawn.match.match_output, 'enable\r\nRouter#')

        r = c.disable()
        self.assertEqual(c.spawn.match.match_output, 'disable\r\nRouter>')

        r = c.enable(command='enable 7')
        self.assertEqual(c.spawn.match.match_output, 'enable 7\r\nRouter#')

        c.disconnect()

    def test_disable_to_enable_with_msg(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state disable_to_enable_with_msg'],
                       os='iosxe',
                       credentials=dict(default=dict(password='cisco')),
                       log_buffer=True
                       )
        c.connect()
        c.disconnect()

    def test_disable_to_enable_no_passwd(self):
        c = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxe --state disable_to_enable_no_passwd'],
            os='iosxe',
            credentials=dict(default=dict(password='cisco')),
            log_buffer=True
        )
        with self.assertRaisesRegex(UniconAuthenticationError, "No password set on this device"):
            c.connect()
        c.disconnect()

    def test_enable_password_handler(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_exec1 --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco'),
                                        enable=dict(password='cisco123')),
                       log_buffer=True
                       )
        try:
            c.connect()
        finally:
            c.disconnect()

    def test_enable_password_handler2(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_login1 --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='notenable', password='cisco'),
                                        enable=dict(password='cisco123')),
                       log_buffer=True
                       )
        try:
            c.connect()
        finally:
            c.disconnect()

    def test_enable_password_handler3(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_exec2 --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='notenable', password='cisco'),
                                        enable=dict(password='cisco2')),
                       log_buffer=True,
                       mit=True
                       )
        try:
            c.connect()
            c.enable(command='enable 2')
        finally:
            c.disconnect()

    def test_disable_pattern(self):
        from unicon.plugins.iosxe.statemachine import IosXESingleRpStateMachine
        from unicon.plugins.iosxe.settings import IosXESettings
        settings = IosXESettings()
        sm = IosXESingleRpStateMachine(learn_hostname=True)
        sm.learn_pattern = settings.DEFAULT_LEARNED_HOSTNAME
        state = sm.get_state('disable')
        match = re.match(state.pattern, 'route(s)  : 0.0.0.0 ->')
        self.assertIsNone(match)
        match = re.match(state.pattern, 'rtr->')
        self.assertIsNotNone(match)

    def test_controller_mode_disable_lowercase_router_prompts(self):
        """Match router> and router# while %N is still the old hostname."""
        c = Connection(
            hostname='C8000V',
            start=[
                'mock_device_cli --os iosxe '
                '--state c8kv_controller_mode_enable --hostname C8000V'
            ],
            os='iosxe',
            operating_mode='Controller-Managed',
            mit=True,
            log_buffer=True,
            connection_timeout=5,
        )
        controller_mode_dialog = Dialog([
            Statement(
                pattern=r'Continue\? \[confirm\]',
                action='sendline()',
                loop_continue=True,
                continue_timer=False,
            ),
            Statement(
                pattern=r'Do you want to abort\? \(yes/\[no\]\):',
                action='sendline(no)',
                loop_continue=True,
                continue_timer=False,
            ),
            Statement(
                pattern=(
                    r'.*Would you like to enter the initial configuration '
                    r'dialog\? \[yes/no\]:\s*'
                ),
                action='sendline(no)',
                loop_continue=True,
                continue_timer=False,
            ),
        ])

        try:
            c.connect()
            c.execute(
                'controller-mode disable',
                service_dialog=controller_mode_dialog,
                allow_state_change=True,
                timeout=5,
            )
            self.assertEqual(c.state_machine.current_state, 'disable')
            self.assertIn('router>', c.spawn.match.match_output)

            # Execute state detection does not relearn %N. The first enable
            # transition therefore must match the explicit default hostname.
            self.assertEqual(c.hostname, 'C8000V')
            c.enable()
            self.assertEqual(c.state_machine.current_state, 'enable')
            self.assertIn('router#', c.spawn.match.match_output)
        finally:
            c.disconnect()

    def test_learn_lowercase_default_router_hostname(self):
        """Learn router when the explicit default-hostname branch matches."""
        c = Connection(
            hostname='C8000V',
            start=[
                'mock_device_cli --os iosxe '
                '--state c8kv_controller_mode_disable'
            ],
            os='iosxe',
            operating_mode='Autonomous',
            learn_hostname=True,
            mit=True,
            log_buffer=True,
            connection_timeout=5,
        )

        try:
            c.connect()
            self.assertEqual(c.hostname, 'router')
            self.assertEqual(c.previous_hostname, 'C8000V')
            self.assertEqual(c.state_machine.current_state, 'disable')
        finally:
            c.disconnect()

class TestIosXEPluginPing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                           start=['mock_device_cli --os iosxe --state isr_exec --hostname Router'],
                           os='iosxe',
                           credentials=dict(default=dict(username='cisco', password='cisco')),
                           log_buffer=True
                           )
        cls.c.connect()

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()

    def test_ping_success_no_vrf(self):
        r = self.c.ping('192.0.0.5', count=30)
        self.maxDiff = None
        self.assertEqual(r.strip(), "\r\n".join("""ping
Protocol [ip]: 
Target IP address: 192.0.0.5
Repeat count [5]: 30
Datagram size [100]: 
Timeout in seconds [2]: 
Extended commands [n]: n
Sweep range of sizes [n]: n
Type escape sequence to abort.
Sending 30, 100-byte ICMP Echos to 192.0.0.5, timeout is 2 seconds:
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Success rate is 100 percent (30/30), round-trip min/avg/max = 1/1/3 ms""".\
splitlines()))

    def test_ping_success_vrf(self):
        r = self.c.ping('192.0.0.6', vrf='test', count=30)
        self.assertEqual(r.strip(), "\r\n".join("""ping vrf test
Protocol [ip]: 
Target IP address: 192.0.0.6
Repeat count [5]: 30
Datagram size [100]: 
Timeout in seconds [2]: 
Extended commands [n]: n
Sweep range of sizes [n]: n
Type escape sequence to abort.
Sending 30, 100-byte ICMP Echos to 192.0.0.6, timeout is 2 seconds:
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Success rate is 100 percent (30/30), round-trip min/avg/max = 1/1/3 ms""".\
splitlines()))

    def test_ping_success_vrf_in_cmd(self):
        r = self.c.ping('192.0.0.6', command='ping vrf test', vrf='dont_use_this_vrf', count=30)
        self.assertEqual(r.strip(), "\r\n".join("""ping vrf test
Protocol [ip]: 
Target IP address: 192.0.0.6
Repeat count [5]: 30
Datagram size [100]: 
Timeout in seconds [2]: 
Extended commands [n]: n
Sweep range of sizes [n]: n
Type escape sequence to abort.
Sending 30, 100-byte ICMP Echos to 192.0.0.6, timeout is 2 seconds:
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Success rate is 100 percent (30/30), round-trip min/avg/max = 1/1/3 ms""".\
splitlines()))


class TestIosxePlugingTraceroute(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(hostname='Router',
                           start=['mock_device_cli --os iosxe --state isr_exec --hostname Router'],
                           os='iosxe',
                           credentials=dict(default=dict(username='cisco', password='cisco')),
                           log_buffer=True
                           )
        cls.c.connect()

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()

    def test_traceroute_success(self):
        r = self.c.traceroute('192.0.0.5', probe=30)
        self.maxDiff = None
        self.assertEqual(r.strip(), "\r\n".join("""traceroute
Protocol [ip]: 
Target IP address: 192.0.0.5
Ingress traceroute [n]: 
Source address or interface: 
DSCP Value [0]: 
Numeric display [n]: 
Timeout in seconds [3]: 
Probe count [3]: 30
Minimum Time to Live [1]: 
Maximum Time to Live [30]: 
Port Number [33434]: 
Loose, Strict, Record, Timestamp, Verbose[none]: 
Type escape sequence to abort.
Tracing the route to 192.0.0.5
VRF info: (vrf in name/id, vrf out name/id)
  1 192.0.0.5 msec *  1 msec""".\
splitlines()))

    def test_traceroute_vrf(self):
        r = self.c.traceroute('192.0.0.5', vrf='MG501', probe=30)
        self.maxDiff = None
        self.assertEqual(r.strip(), "\r\n".join("""traceroute vrf MG501
Protocol [ip]: 
Target IP address: 192.0.0.5
Ingress traceroute [n]: 
Source address or interface: 
DSCP Value [0]: 
Numeric display [n]: 
Timeout in seconds [3]: 
Probe count [3]: 30
Minimum Time to Live [1]: 
Maximum Time to Live [30]: 
Port Number [33434]: 
Loose, Strict, Record, Timestamp, Verbose[none]: 
Type escape sequence to abort.
Tracing the route to 192.0.0.5
VRF info: (vrf in name/id, vrf out name/id)
  1 192.0.0.5 msec *  1 msec""".\
splitlines()))


class TestIosXEluginBashService(unittest.TestCase):

    def test_terminal_position_handler(self):
        """Test that terminal_position_handler sends correct VT100 cursor
        position response ESC[0;0R without any additional cleanup."""
        mock_spawn = MagicMock()
        mock_session = {}
        mock_context = {}

        terminal_position_handler(mock_spawn, mock_session, mock_context)

        # Verify the handler sent only the cursor position response
        mock_spawn.send.assert_called_once_with('\x1b[0;0R')

    def test_bash(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state isr_exec --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )
        with c.bash_console() as console:
            console.execute('ls')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('Router#', c.spawn.match.match_output)
        c.disconnect()

    def test_bash_asr(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state asr_exec --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )
        with c.bash_console() as console:
            console.execute('df /bootflash/')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('Router#', c.spawn.match.match_output)
        c.disconnect()

    def test_bash_standby(self):
        c = Connection(hostname='R1',
                       start=['mock_device_cli --os iosxe --state general_enable --hostname R1'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )
        with c.bash_console(switch='standby', rp='active') as console:
            console.execute('ls')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('R1#', c.spawn.match.match_output)
        c.disconnect()

    def test_bash_chassis_active(self):
        c = Connection(hostname='WLC1',
                       start=['mock_device_cli --os iosxe --state general_enable --hostname WLC1'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True)
        with c.bash_console(chassis='active r0') as console:
            console.execute('ls')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('WLC1#', c.spawn.match.match_output)
        c.disconnect()

    def test_bash_chassis_standby(self):
        c = Connection(hostname='WLC1',
                       start=['mock_device_cli --os iosxe --state general_enable --hostname WLC1'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True)
        with c.bash_console(chassis='standby r0') as console:
            console.execute('ls')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('WLC1#', c.spawn.match.match_output)
        c.disconnect()

    def test_bash_disable_selinux(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_enable --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )
        with c.bash_console(disable_selinux=True) as console:
            self.assertIn('[Router_RP_0:/]$', c.spawn.match.match_output)
            console.execute('df /bootflash/')
        self.assertIn('set platform software selinux default', c.spawn.match.match_output)
        self.assertIn('Router#', c.spawn.match.match_output)
        c.disconnect()

    def test_bash_disable_selinux_invalid_cmds(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state enable_isr --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )
        with c.bash_console(disable_selinux=True) as console:
            self.assertIn('[Router:/]$', c.spawn.match.match_output)
            console.execute('ls')
        self.assertIn('set platform software selinux default', c.spawn.match.match_output)
        self.assertIn('Router#', c.spawn.match.match_output)
        c.disconnect()

    def test_bash_parse(self):
        testbed = '''
            devices:
                R1:
                    os: iosxe
                    connections:
                        defaults:
                            class: 'unicon.Unicon'
                        cli:
                            command: mock_device_cli --os iosxe --state general_enable --hostname R1
        '''
        tb = loader.load(testbed)
        dev = tb.devices.R1
        try:
            dev.connect(mit=True, log_buffer=True)
            with dev.bash_console() as console:
                output = console.parse('ls -l')
            expected_output = {
                'files': {'bin': {'day': 10,
                    'filename': 'bin',
                    'group': 'root',
                    'linked_filename': 'usr/bin',
                    'links': 1,
                    'mode': 'lrwxrwxrwx.',
                    'month': 'Sep',
                    'size': 7,
                    'user': 'root',
                    'year': 2024},
                'boot': {'day': 9,
                        'filename': 'boot',
                        'group': 'root',
                        'hour': 20,
                        'links': 2,
                        'minute': 41,
                        'mode': 'drwxr-xr-x.',
                        'month': 'Jan',
                        'size': 60,
                        'user': 'root'}},
                'total': 55000
            }
            self.assertEqual(output, expected_output)
        finally:
            dev.disconnect()


class TestIosXESDWANConfigure(unittest.TestCase):

    def test_config_transaction(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state sdwan_enable --hostname Router'],
                       os='iosxe', platform='sdwan',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )

        d.connect()
        d.configure('no logging console')
        d.disconnect()

    def test_config_transaction_sdwan_iosxe(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state sdwan_enable --hostname Router'],
                       os='sdwan', platform='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )

        d.connect()
        d.configure('no logging console')
        d.disconnect()

    def test_config_transaction_sdwan_iosxe_confirm(self):
        d = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state sdwan_enable2 --hostname Router'],
                       os='iosxe', platform='sdwan',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True,
                       mit=True
                       )

        d.connect()
        d.configure('no logging console')
        d.disconnect()


class TestIosXEControllerTransactionConfigure(unittest.TestCase):

    def test_config_to_enable_discards_uncommitted_changes(self):
        connection = Connection(
            hostname='Router',
            start=[
                'mock_device_cli --os iosxe '
                '--state controller_transaction_enable --hostname Router'
            ],
            os='iosxe',
            credentials=dict(
                default=dict(username='cisco', password='cisco')),
            log_buffer=True,
            mit=True,
        )

        try:
            connection.connect()
            connection.configure('no logging console')
            self.assertEqual(
                connection.state_machine.current_state, 'enable')
        finally:
            connection.disconnect()


class TestIosXECat9kPluginReload(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='switch',
            start=['mock_device_cli --os iosxe --state general_enable --hostname switch'],
            os='iosxe',
            platform='cat9k',
            credentials=dict(default=dict(
                username='cisco', password='cisco', enable_password='Secret12345!')),
            log_buffer=True,
            mit=True
            )
        cls.c.connect()

    @classmethod
    def tearDownClass(cls):
         cls.c.disconnect()

    def test_reload1(self):
         self.c.reload(reload_command='reload1', post_reload_wait_time=1)
         self.assertEqual(self.c.reload.post_reload_wait_time, 1)

class TestIosXECat3kPluginReload(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='switch',
            start=['mock_device_cli --os iosxe --state cat3k_exec --hostname switch'],
            os='iosxe',
            platform='cat3k',
            credentials=dict(default=dict(
                username='cisco', password='cisco'),
                alt=dict(
                username='admin', password='lab')),
            log_buffer=True
            )

        cls.c.connect()

    @classmethod
    def tearDownClass(cls):
         cls.c.disconnect()
    def test_reload(self):
        self.c.reload()


class TestIosXEDiol(unittest.TestCase):

    def test_connection(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state standby_exec --hostname Router'],
                       os='iosxe',
                       init_exec_commands=[],
                       init_config_commands=[],
                       credentials=dict(default=dict(
                       username='cisco', password='cisco'),
                       alt=dict(
                       username='admin', password='lab')),
                       log_buffer=True
                       )

        c.connect()
        c.disconnect()

    def test_connection_diol_exec(self):
        c = Connection(hostname='RouterRP',
                       start=['mock_device_cli --os iosxe --state diol_exec --hostname RouterRP'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       credentials=dict(default=dict(
                       username='cisco', password='cisco'),
                       alt=dict(
                       username='admin', password='lab')),
                       log_buffer=True
                       )

        c.connect()
        c.disconnect()

    def test_connection_diol_enable(self):
        c = Connection(hostname='RouterRP',
                       start=['mock_device_cli --os iosxe --state diol_enable --hostname RouterRP'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       credentials=dict(default=dict(
                       username='cisco', password='cisco'),
                       alt=dict(
                       username='admin', password='lab')),
                       log_buffer=True
                       )

        c.connect()
        c.disconnect()

    def test_connection_diol_disable(self):
        c = Connection(hostname='RouterRP',
                       start=['mock_device_cli --os iosxe --state diol_disable --hostname RouterRP'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       credentials=dict(default=dict(
                       username='cisco', password='cisco'),
                       alt=dict(
                       username='admin', password='lab')),
                       log_buffer=True
                       )

        c.connect()
        c.disconnect()


class TestIosXEConfigure(unittest.TestCase):

    def test_configure_cert_trustpool(self):
        c = Connection(hostname='RouterRP',
                       start=['mock_device_cli --os iosxe --state general_config --hostname RouterRP'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True
                       )
        c.connect()
        c.configure(['crypto pki certificate pool', 'cabundle nvram:ios_core.p7b'])
        c.disconnect()

    def test_configure_are_you_sure_ywtdt(self):
        c = Connection(hostname='RouterRP',
                       start=['mock_device_cli --os iosxe --state general_enable --hostname RouterRP'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True
                       )
        c.connect()
        c.configure(['crypto pki trustpoint test', 'no crypto pki trustpoint test'])
        c.disconnect()

    def test_configure_error_pattern(self):
        c = Connection(hostname='RouterRP',
                       start=['mock_device_cli --os iosxe --state general_enable --hostname RouterRP'],
                       os='iosxe',
                       init_exec_commands=[],
                       log_buffer=True
                       )
        c.connect()
        for cmd in ['ntp server vrf foo 1.2.3.4']:
          with self.assertRaises(SubCommandFailure) as err:
              r = c.configure(cmd)
        c.disconnect()

    def test_password_validation_error_pattern(self):
        c = Connection(hostname='RouterRP',
                       start=['mock_device_cli --os iosxe --state general_enable --hostname RouterRP'],
                       os='iosxe',
                       init_exec_commands=[],
                       log_buffer=True
                       )
        c.connect()
        with self.assertRaises(SubCommandFailure):
            c.configure('username admin privilege 15 password Secret12345')
        c.disconnect()

    def test_configure_with_msgs(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='config_with_msgs')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            credentials=dict(default=dict(username='cisco', password='cisco')),
            mit=True,
        )
        try:
            c.connect()
            c.configure('msg')
        finally:
            c.disconnect()
            md.stop()

    def test_configure_with_msgs2(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='config_with_msgs2')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            credentials=dict(default=dict(username='cisco', password='cisco')),
            mit=True
        )
        try:
            c.connect()
            c.configure('msg')
        finally:
            c.disconnect()
            md.stop()

    def test_config_locked(self):
        c = Connection(hostname='RouterRP',
                       start=['mock_device_cli --os iosxe --state general_enable --hostname RouterRP'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True
                       )
        c.connect()

        c.execute('set config lock count 2')
        c.settings.CONFIG_LOCK_RETRIES = 0
        c.settings.CONFIG_LOCK_RETRY_SLEEP = 0

        with self.assertRaises(StateMachineError):
            c.configure('')

        c.execute('set config lock count 2')
        with self.assertRaises(StateMachineError):
            c.configure('', lock_retries=1, lock_retry_sleep=1)

        c.execute('set config lock count 3')
        c.settings.CONFIG_LOCK_RETRIES = 1
        c.settings.CONFIG_LOCK_RETRY_SLEEP = 1
        with self.assertRaises(StateMachineError):
            c.configure('')

        c.execute('set config lock count 3')
        c.settings.CONFIG_LOCK_RETRIES = 5
        c.settings.CONFIG_LOCK_RETRY_SLEEP = 1
        c.configure('')

        c.disconnect()

    def test_slow_config_mode(self):
        c = Connection(hostname='Switch',
                       start=['mock_device_cli --os iosxe --state slow_config_mode --hostname Switch'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True
                       )
        c.connect()
        c.configure(['no logging console'])
        c.disconnect()

    def test_slow_config_mode2(self):
        c = Connection(hostname='Switch',
                       start=['mock_device_cli --os iosxe --state slow_config_mode2 --hostname Switch'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True,
                       settings=dict(CONFIG_TIMEOUT=10),
                       debug=True
                       )
        c.connect()
        c.configure(['no logging console'])
        c.disconnect()

    def test_slow_config_lock(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='config_locked')
        md.start()

        c = Connection(
            hostname='Router',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            mit=True,
            log_buffer=True,
        )
        try:
            c.connect()
            c.settings.CONFIG_TIMEOUT=5
            c.settings.CONFIG_LOCK_RETRY_SLEEP=3
            c.configure(['no logging console'])
        finally:
            c.disconnect()
            md.stop()

    def test_config_no_service_prompt_config(self):
        c = Connection(hostname='Switch',
                       start=['mock_device_cli --os iosxe --state enable_no_service_prompt_config --hostname Switch'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True
                       )
        c.connect()
        c.configure(['no logging console'])
        c.disconnect()

    def test_configure_host_list(self):
        c = Connection(hostname='Switch',
                       start=['mock_device_cli --os iosxe --state general_enable'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True
                       )
        c.connect()
        try:
            c.configure(['ip host-list host1'])
        finally:
            c.disconnect()


    def test_configure_macro(self):
        c = Connection(hostname='Switch',
                       start=['mock_device_cli --os iosxe --state general_enable'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True
                       )
        c.connect()
        cfg = [
            "macro auto execute TEST {",
            "if [[ $LINKUP == YES ]]",
            "then conf t",
            "end",
            "fi",
            "}"
        ]
        try:
            c.configure(cfg)
        finally:
            c.disconnect()

    def test_configure_trailing_prompt_stripping(self):
        c = Connection(hostname='Switch',
                       start=['mock_device_cli --os iosxe --state general_enable'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True
                       )
        config_service = c.configure

        con_state = 'config'
        pattern = re.compile(c.state_machine.get_state('config').pattern, flags=re.S)

        output = 'help\r\nSwitch(ca-trustpoint)#'

        result = output
        result_match = ExpectMatch()
        result_match.last_match = pattern.match(output)
        result_match.last_match_index = 1
        result_match.last_match_mode = MatchMode(mode_id=1, mode_name='search only last line')
        result_match.match_output = output

        new_result = config_service.utils.truncate_trailing_prompt(
            con_state,
            result,
            hostname='Switch',
            result_match=result_match
        )
        self.assertEqual(new_result, 'help\r\n')

        new_result = config_service.utils.truncate_trailing_prompt(
            con_state,
            result,
            hostname='PE1',
            result_match=result_match
        )
        self.assertEqual(new_result, 'help\r\nSwitch(ca-trustpoint)#')

    def test_configure_wsma_agent_exec(self):
        c = Connection(hostname='Switch',
                       start=['mock_device_cli --os iosxe --state general_enable'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True
                       )
        c.connect()
        c.configure('wsma agent exec')
        c.disconnect()

    def test_configure_pki_hexmode(self):
        c = Connection(hostname='Switch',
                       start=['mock_device_cli --os iosxe --state general_enable'],
                       os='iosxe',
                       mit=True,
                       init_exec_commands=[],
                       init_config_commands=[],
                       log_buffer=True,
                       )
        try:
            c.connect()
            c.configure(['crypto pki certificate chain SLA-TrustPoint', 'certificate ca 01'])
        finally:
            c.disconnect()
                   
class TestIosXEEnableSecret(unittest.TestCase):

    def test_enable_secret(self):
        c = Connection(hostname='R1',
                       start=['mock_device_cli --os iosxe --state initial_config_dialog --hostname R1'],
                       os='iosxe',
                       init_exec_commands=[],
                       init_config_commands=[],
                       credentials=dict(default=dict(password='Secret12345!')),
                       log_buffer=True
                       )
        c.connect()
        c.configure(['no logging console'])
        c.disconnect()

    def test_bad_enable_secret(self):
        c = Connection(hostname='R1',
                       start=['mock_device_cli --os iosxe --state initial_config_dialog --hostname R1'],
                       os='iosxe',
                       init_exec_commands=[],
                       init_config_commands=[],
                       credentials=dict(default=dict(password='veryverybadpw')),
                       log_buffer=True
                       )
        with self.assertRaisesRegex(UniconAuthenticationError, 'Too many enable password retries'):
            c.connect()
        c.disconnect()

    def test_enable_secret_topology_legacy(self):
        tb = loader.load("""
        devices:
          R1:
            os: iosxe
            passwords:
                enable: Secret12345!
            connections:
              cli:
                command: mock_device_cli --os iosxe --state initial_config_dialog --hostname R1
                arguments:
                  log_buffer: True
                  init_exec_commands: []
                  init_config_commands: []
        """)
        dev = tb.devices.R1
        dev.connect()
        dev.disconnect()

    def test_enable_secret_topology(self):
        tb = loader.load("""
        devices:
          R1:
            os: iosxe
            credentials:
              default:
                password: Secret12345!
            connections:
              cli:
                command: mock_device_cli --os iosxe --state initial_config_dialog --hostname R1
                arguments:
                  log_buffer: True
                  init_exec_commands: []
                  init_config_commands: []
        """)
        dev = tb.devices.R1
        try:
            output = dev.connect()
            self.assertIn('Enter your selection [2]: 2\r\n', output)
        finally:
            dev.disconnect()

    def test_enable_secret_no_password(self):
        self.maxDiff = None
        c = Connection(hostname='R1',
                       start=['mock_device_cli --os iosxe --state initial_config_dialog --hostname R1'],
                       os='iosxe',
                       init_exec_commands=[],
                       init_config_commands=[],
                       credentials=dict(default=dict(password='')),
                       log_buffer=True
                       )
        try:
            output = c.connect()
            self.assertIn('Enter your selection [2]: \n0', output)
        finally:
            c.disconnect()

    def test_enable_secret_short_password(self):
        self.maxDiff = None
        c = Connection(hostname='R1',
                       start=['mock_device_cli --os iosxe --state initial_config_dialog --hostname R1'],
                       os='iosxe',
                       init_exec_commands=[],
                       init_config_commands=[],
                       credentials=dict(default=dict(password='lab')),
                       log_buffer=True
                       )
        try:
            output = c.connect()
            self.assertIn('Enter your selection [2]: \n0', output)
        finally:
            c.disconnect()


class TestIosXEluginGuestShellService(unittest.TestCase):

    def test_guestshell(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_enable --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )
        with c.guestshell() as console:
            output = console.execute('pwd')
            self.assertEqual(output, '/home/guestshell')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('Router#', c.spawn.match.match_output)
        c.disconnect()

    def test_guestshell_activate(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state general_enable --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True
                       )
        with c.guestshell(enable_guestshell=True) as console:
            output = console.execute('pwd')
            self.assertEqual(output, '/home/guestshell')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('Router#', c.spawn.match.match_output)
        c.disconnect()

    def test_guestshell_activate_configure(self):
        c = Connection(hostname='Router',
                       start=['mock_device_cli --os iosxe --state enable_guestshell --hostname Router'],
                       os='iosxe',
                       credentials=dict(default=dict(username='cisco', password='cisco')),
                       log_buffer=True,
                       mit=True
                       )
        with c.guestshell(enable_guestshell=True) as console:
            output = console.execute('pwd')
            self.assertEqual(output, '/home/guestshell')
        self.assertIn('exit', c.spawn.match.match_output)
        self.assertIn('Router#', c.spawn.match.match_output)
        c.disconnect()

class TestIosXEping(unittest.TestCase):

    def test_ping_failed_protocol(self):
        md = MockDeviceTcpWrapperIOSXE(hostname='PE1', port=0, state='ping_fail')
        md.start()

        c = Connection(
            hostname='PE1',
            start=['telnet 127.0.0.1 {}'.format(md.ports[0])],
            os='iosxe',
            connection_timeout=10,
            mit=True
        )
        try:
            c.connect()
            try:
                c.ping('10.10.10.10')
            except Exception:
                pass
            c.configure()
        except Exception:
            raise
        finally:
            c.disconnect()
            md.stop()


class TestSyslogHandler(unittest.TestCase):

    def test_syslog_handler_timeout(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state endless_syslog --hostname PE1'],
            os='iosxe',
            connection_timeout=5,
            settings=dict(PROMPT_RECOVERY_COMMANDS = ['\x06']),
            prompt_recovery=True
        )
        try:
            c.connect()
        except Exception:
            raise
        finally:
            c.disconnect()

    def test_syslog_handler_error_opening_pattern(self):
        d = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxe --state error_opening_syslog --hostname Router'],
            os='iosxe',
            credentials=dict(default=dict(username='cisco', password='cisco')),
            log_buffer=True
        )

        d.connect()
        d.disconnect()

    def test_syslog_handler_guestshell(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state guestshell_prompt_obscure_enable --hostname PE1'],
            os='iosxe',
            mit=True,
        )
        try:
            c.connect()
            c.execute('show version')
        except Exception:
            raise
        finally:
            c.disconnect()

    def test_handler_ddns_pattern(self):
        d = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxe --state ip_ddns_update_method --hostname Router'],
            os='iosxe',
            credentials=dict(default=dict(username='cisco', password='cisco')),
            log_buffer=True
        )

        try:
            d.connect()
        finally:
            d.disconnect()
    

    def test_reload_security_log_message(self):
        d = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxe --state enable_reload_security_log1 --hostname Router'],
            os='iosxe',
            credentials=dict(default=dict(username='cisco', password='cisco')),
            log_buffer=True,
            mit=True,
        )
        try:
            d.connect()
            d.reload(post_reload_wait_time=3)
        finally:
            d.disconnect()

    def test_reload_RSA_key_log_message(self):
        d = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxe --state enable_reload_RSA_log1 --hostname Router'],
            os='iosxe',
            credentials=dict(default=dict(username='cisco', password='cisco')),
            log_buffer=True,
            mit=True,
        )
        try:
            d.connect()
            d.reload(post_reload_wait_time=3)
        finally:
            d.disconnect()

    def test_reload_Insecure_log_message(self):
        d = Connection(
            hostname='Router',
            start=['mock_device_cli --os iosxe --state enable_reload_insecure_log1 --hostname Router'],
            os='iosxe',
            credentials=dict(default=dict(username='cisco', password='cisco')),
            log_buffer=True,
            mit=True,
        )
        try:
            d.connect()
            d.reload(post_reload_wait_time=3)
        finally:
            d.disconnect()


class TestIosxeAsr1k(unittest.TestCase):
    def test_connect_asr1k_ha(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='ha_asr1k_exec,ha_asr1k_stby_exec', hostname='R1')
        md.start()

        c = Connection(
            hostname='R1',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1])
            ],
            os='iosxe',
            connection_timeout=10,
            mit=True
        )
        try:
            c.connect()
        except Exception:
            raise
        finally:
            c.disconnect()
            md.stop()

    def test_connect_asr1k_ha_rommon(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='ha_asr1k_exec,ha_asr1k_stby_exec', hostname='R1')
        md.start()

        c = Connection(
            hostname='R1',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1])
            ],
            os='iosxe',
            connection_timeout=10,
            credentials=dict(default=dict(password='lab'))
        )
        try:
            c.connect()
            c.execute('reload_to_rommon')
            c.rommon()
            c.enable(target='active')
            c.enable(target='standby')
        except Exception:
            raise
        finally:
            c.disconnect()
            md.stop()

    def test_connect_asr1k_ha_rommon_boot_image(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='ha_asr1k_exec,ha_asr1k_stby_exec', hostname='R1')
        md.start()

        c = Connection(
            hostname='R1',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1])
            ],
            os='iosxe',
            connection_timeout=10,
            credentials=dict(default=dict(password='lab'))
        )
        try:
            c.connect()
            c.execute('reload_to_rommon')
            c.rommon()
            c.enable(target='active', image='test/packages.conf')
            c.enable(target='standby', image='test/packages.conf')

            c.execute('reload_to_rommon')
            c.rommon()
            c.enable(target='active', image_to_boot='test/packages.conf')
            c.enable(target='standby', image_to_boot='test/packages.conf')
        except Exception:
            raise
        finally:
            c.disconnect()
            md.stop()


class TestIosxeTclsh(unittest.TestCase):

    def test_tclsh(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()
        c.tclsh()
        c.enable()
        c.disconnect()

    def test_tclsh_long_hostname(self):
        c = Connection(
            hostname='very-very-long-hostname',
            start=['mock_device_cli --os iosxe --state general_enable --hostname very-very-long-hostname'],
            os='iosxe',
            mit=True
        )
        c.connect()
        c.execute('long_hostname')
        c.tclsh()
        c.enable()
        c.disconnect()

    def test_tclsh_continue(self):
        c = Connection(
            hostname='R1',
            start=['mock_device_cli --os iosxe --state tclsh_continue --hostname R1'],
            os='iosxe',
            mit=True
        )
        try:
            c.connect()
        finally:
            c.disconnect()


class TestIosxeAcmConfigure(unittest.TestCase):

    def test_acm_configure(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()
        config_txt = [
            'interface loopback 1',
            'description test'
        ]
        c.configure(config_txt, acm_configlet='my_config')
        c.disconnect()

    def test_ha_acm_configure(self):
        md = MockDeviceTcpWrapperIOSXE(port=0, state='ha_cat9k_exec,ha_cat9k_stby_exec', hostname='R1')
        md.start()

        c = Connection(
            hostname='R1',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1])
            ],
            os='iosxe',
            connection_timeout=10,
            credentials=dict(default=dict(password='lab'))
        )
        try:
            c.connect()
            config_txt = [
            'interface loopback 1',
            'description test'
            ]
            c.configure(config_txt, acm_configlet='my_config')
        except Exception:
            raise
        finally:
            c.disconnect()
            md.stop()

class TestIosxeAcmRulesConfigure(unittest.TestCase):

    def test_acm_rules_configure(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()
        config_txt = [
            'match mode mdt-subscription-mode command no',
            'match mode interface command no ip address 10.43.188.58 255.255.255.192',
            'action pre-apply'
        ]
        c.configure(config_txt, rules=True)
        c.disconnect()


class TestIosxeAcmConfigureInvalidInput(unittest.TestCase):

    def test_acm_configure_invalid_input(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()
        config_txt = [
            'interface loopback 1',
            'description test',
            'invalid command example',  # this should trigger % Invalid input
            'description test1'
        ]
        with self.assertRaises(SubCommandFailure):
            c.configure(config_txt, acm_configlet='my_config')
        self.assertEqual(
            c.state_machine.current_state,
            'enable',
            f"Device not recovered to exec mode after invalid input, current: {c.state_machine.current_state}"
        )
        c.disconnect()


class TestIosxeAcmInvalidCommand(unittest.TestCase):

    def test_invalid_command_configure(self):
        """Test plain configure after failed ACM - should not enter ACM mode"""
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()

        config_txt_fail = [
            'interface loopback 1',
            'invalid command example', #invalid commad
        ]
        with patch.object(c.spawn, 'sendline', wraps=c.spawn.sendline) as mock_sendline_fail:
            with self.assertRaises(SubCommandFailure):
                c.configure(config_txt_fail, acm_configlet='my_config')

        sent_fail = [call.args[0] for call in mock_sendline_fail.call_args_list if call.args]
        expected_fail = ['acm configlet create my_config', 'interface loopback 1', 'invalid command example', 'end']
        self.assertEqual(sent_fail, expected_fail, f"Expected commands {expected_fail}, but got {sent_fail}")

        config_txt_plain = ['interface loopback 2', 'description test']
        with patch.object(c.spawn, 'sendline', wraps=c.spawn.sendline) as mock_sendline_plain:
            c.configure(config_txt_plain)

        sent_plain = [call.args[0] for call in mock_sendline_plain.call_args_list if call.args]
        expected_plain = ['config term', 'interface loopback 2', 'description test', 'end']
        self.assertEqual(sent_plain, expected_plain, f"Expected commands {expected_plain}, but got {sent_plain}")
        self.assertNotIn('acm configlet create my_config', sent_plain)

        c.disconnect()


class TestConfigureEmptySpacesHandling(unittest.TestCase):

    def test_configure_with_leading_trailing_spaces(self):
        """Test configure commands with leading and trailing spaces"""
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()

        config_txt = [
            " ",
            "  interface loopback 1  ",
            "description test device",
            " no shutdown  "  # Leading space
        ]

        with patch.object(c.spawn, 'sendline', wraps=c.spawn.sendline) as mock_sendline:
            c.configure(config_txt)

        sent_commands = [call.args[0] for call in mock_sendline.call_args_list if call.args]
        # Validate exact expected commands with preserved leading/trailing spaces
        expected_config = ['config term', ' ', '  interface loopback 1  ', 'description test device', ' no shutdown  ', 'end']
        self.assertEqual(sent_commands, expected_config, f"Expected {expected_config}, but got {sent_commands}")
        self.assertEqual(
            c.state_machine.current_state,
            'enable',
            f"Device should be in enable state, but is in {c.state_machine.current_state}"
        )

        c.disconnect()

class TestBannerWithPreCommands(unittest.TestCase):

    def test_banner_login_with_pre_commands(self):
        """Test banner login configuration with pre-commands before banner content"""
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()

        config_txt = (
            "vrf definition Mgmt\n"
            "banner login *\n"
            "\n"
            "Updated - Unauthorized access to this device is strictly prohibited.\n"
            "\n"
            "Please contact corpnet@fb.com with any access requests.\n"
            "Done\n"
            "\n"
            "*"
        )
        with patch.object(c.spawn, 'sendline', wraps=c.spawn.sendline) as mock_sendline:
            c.configure(config_txt)

        sent_commands = [call.args[0] for call in mock_sendline.call_args_list if call.args]
        # Check complete list of expected commands including empty lines
        expected_commands = ['config term', 'vrf definition Mgmt', 'banner login *', '', 
                           'Updated - Unauthorized access to this device is strictly prohibited.', '',
                           'Please contact corpnet@fb.com with any access requests.', 'Done', '', '*', 'end']
        self.assertEqual(sent_commands, expected_commands, f"Expected exact command sequence {expected_commands}, but got {sent_commands}")

        c.disconnect()

class TestIosxeSyntaxConfigure(unittest.TestCase):

    def test_syntax_configure(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()
        config_txt = [
            'interface loopback 1',
            'description test'
        ]
        with patch.object(
                c.spawn, 'sendline', wraps=c.spawn.sendline) as sendline:
            c.configure(config_txt, config_syntax_check=True)
        self.assertEqual(c.state_machine.current_state, 'enable')
        self.assertEqual(sendline.call_args_list, [
            unittest.mock.call('config check syntax'),
            unittest.mock.call('interface loopback 1'),
            unittest.mock.call('description test'),
            unittest.mock.call('end'),
        ])
        c.disconnect()


class TestIosxeMultipleBannerConfigure(unittest.TestCase):

    def test_multiple_banner_configure(self):
        """
        Test that device.configure is called correctly for basic
        banner configuration without an ACM configlet.
        This test now asserts on the 'mock data' passed to configure.
        """
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_config --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()
        banner_config ='''
banner login *
Updated - Unauthorized access to this device is strictly prohibited.
Please contact corpnet@fb.com with any access requests.
Done
*
'''

        c.configure(banner_config)
        c.disconnect()


class TestIosxeConfigSyntaxService(unittest.TestCase):

    def test_single_rp_config_syntax_service(self):
        c = Connection(
            hostname='PE1',
            start=[
                'mock_device_cli --os iosxe --state general_enable '
                '--hostname PE1'
            ],
            os='iosxe',
            mit=True
        )
        c.connect()
        try:
            with patch.object(
                    c.spawn, 'sendline', wraps=c.spawn.sendline) as sendline:
                c.config_syntax([
                    'interface loopback 1',
                    'description test',
                ])
            self.assertEqual(c.state_machine.current_state, 'enable')
            self.assertEqual(sendline.call_args_list, [
                unittest.mock.call('config check syntax'),
                unittest.mock.call('interface loopback 1'),
                unittest.mock.call('description test'),
                unittest.mock.call('end'),
            ])
        finally:
            c.disconnect()

    def test_dual_rp_config_syntax_service(self):
        md = MockDeviceTcpWrapperIOSXE(
            port=0,
            state='ha_asr1k_exec,ha_asr1k_stby_exec',
            hostname='R1')
        md.start()
        c = Connection(
            hostname='R1',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1]),
            ],
            os='iosxe',
            connection_timeout=10,
            credentials=dict(default=dict(password='lab')),
        )
        try:
            c.connect()
            with patch.object(
                    c.active.spawn,
                    'sendline',
                    wraps=c.active.spawn.sendline) as sendline:
                c.config_syntax([
                    'interface loopback 1',
                    'description syntax test',
                ])
            self.assertEqual(c.active.state_machine.current_state, 'enable')
            self.assertEqual(sendline.call_args_list, [
                unittest.mock.call('config check syntax'),
                unittest.mock.call('interface loopback 1'),
                unittest.mock.call('description syntax test'),
                unittest.mock.call('end'),
            ])
        finally:
            c.disconnect()
            md.stop()

    def test_syntax_configlet_rejected_single_rp(self):
        c = Connection(
            hostname='PE1',
            start=[
                'mock_device_cli --os iosxe --state general_enable '
                '--hostname PE1'
            ],
            os='iosxe',
            mit=True
        )
        c.connect()
        try:
            with patch.object(
                    c.spawn, 'sendline', wraps=c.spawn.sendline) as sendline:
                with self.assertRaises(SubCommandFailure):
                    c.configure('interface loopback 1',
                                syntax_configlet='my_config')
            sent = [call.args[0] for call in sendline.call_args_list
                    if call.args]
            self.assertNotIn('config term', sent)
        finally:
            c.disconnect()

    def test_syntax_configlet_rejected_dual_rp(self):
        md = MockDeviceTcpWrapperIOSXE(
            port=0,
            state='ha_asr1k_exec,ha_asr1k_stby_exec',
            hostname='R1')
        md.start()
        c = Connection(
            hostname='R1',
            start=[
                'telnet 127.0.0.1 {}'.format(md.ports[0]),
                'telnet 127.0.0.1 {}'.format(md.ports[1]),
            ],
            os='iosxe',
            connection_timeout=10,
            credentials=dict(default=dict(password='lab')),
        )
        try:
            c.connect()
            with patch.object(
                    c.active.spawn,
                    'sendline',
                    wraps=c.active.spawn.sendline) as sendline:
                with self.assertRaises(SubCommandFailure):
                    c.configure('interface loopback 1',
                                syntax_configlet='my_config')
            sent = [call.args[0] for call in sendline.call_args_list
                    if call.args]
            self.assertNotIn('config term', sent)
        finally:
            c.disconnect()
            md.stop()


class TestIosxeBannerACM(unittest.TestCase):
    '''
    Testcase to test banner using acm terminal input.
    '''
    def test_banner_acm(self):
        """
        Test to configure banner using acm.
        """
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()
        bnr = '''
banner login %
Updated - Unauthorized access to this device is strictly prohibited.
Please contact corpnet@fb.com with any access requests.
Done
%
'''

        c.configure(bnr, acm_configlet='my_config')
        c.disconnect()


class TestIosxeMultipleBannersInSingleConfigure(unittest.TestCase):
    """Test that multiple banner blocks in a single configure call are all
    handled correctly without deadlock/timeout."""

    def test_two_banners_exec_and_login(self):
        """Two banners (exec + login) with pre/post commands in one configure call."""
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()

        config_txt = (
            "banner login *\n"
            "\n"
            "Updated - Unauthorized access to this device is strictly prohibited.\n"
            "\n"
            "Please contact corpnet@fb.com with any access requests.\n"
            "Done\n"
            "\n"
            "*"
            "\n"
            "banner login %\n"
            "\n"
            "ENG Systems and Solutions Team Administered device.\n"
            "\n"
            "Only Admins have PRIV-15 Login.\n"
            "Done\n"
            "%\n"
        )

        with patch.object(c.spawn, 'sendline', wraps=c.spawn.sendline) as mock_sendline:
            c.configure(config_txt)

        sent = [call.args[0] for call in mock_sendline.call_args_list if call.args]
        # Check complete list of expected commands including empty lines for BOTH banners
        expected_commands = ['config term', 'banner login *', '',
                           'Updated - Unauthorized access to this device is strictly prohibited.', '',
                           'Please contact corpnet@fb.com with any access requests.', 'Done', '', '*',
                           'banner login %', '',
                           'ENG Systems and Solutions Team Administered device.', '',
                           'Only Admins have PRIV-15 Login.', 'Done', '%',
                           'end']
        self.assertEqual(sent, expected_commands, f"Expected exact command sequence {expected_commands}, but got {sent}")

        c.disconnect()

class TestConfigTransition(unittest.TestCase):

    def test_config_transition_setting(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()
        self.assertEqual(c.settings.CONFIG_TRANSITION_WAIT, 0.2)
        self.assertEqual(c.spawn.settings.CONFIG_TRANSITION_WAIT, 0.2)
        c.configure()
        c.settings.CONFIG_TRANSITION_WAIT = 1
        c.configure()
        self.assertEqual(c.settings.CONFIG_TRANSITION_WAIT, 1)
        self.assertEqual(c.spawn.settings.CONFIG_TRANSITION_WAIT, 1)
        c.disconnect()

    def test_config_transition_learn_hostname(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state enable_slow_config --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()
        # Force hostname learning to be enabled so default prompt pattern is used
        # This was causing issues and should not fail with this test
        c.state_machine.learn_hostname = True
        c.configure()


class TestRommonCommands(unittest.TestCase):

    def test_rommon_command_false_prompt_avoidance(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state rommon_command_output_not_a_prompt --hostname PE1'],
            os='iosxe',
            learn_hostname=True,
            credentials=dict(default=dict(username='cisco', password='cisco')),
            settings={'ROMMON_INIT_COMMANDS': ['notaprompt'], 'EXECUTE_STATE_CHANGE_MATCH_RETRY_SLEEP': 3}
        )
        try:
            c.connect()
        finally:
            c.disconnect()

    def test_rommon_command_false_prompt(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state rommon_command_output_not_a_prompt2 --hostname PE1'],
            os='iosxe',
            learn_hostname=True,
            credentials=dict(default=dict(username='cisco', password='cisco')),
            settings={
                'ROMMON_INIT_COMMANDS': ['notaprompt'],
                'EXECUTE_STATE_CHANGE_MATCH_RETRIES': 0,
                'EXECUTE_STATE_CHANGE_MATCH_RETRY_SLEEP': 1
            },
            debug=True
        )
        with self.assertRaisesRegex(UniconConnectionError,
            "Expected device to reach 'rommon' state, but landed on 'enable' state."):
            try:
                c.connect()
            finally:
                c.disconnect()


class TestCopy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            mit=True
        )
        cls.c.connect()

    @classmethod
    def tearDownClass(cls):
        cls.c.disconnect()

    def test_copy(self):
        self.c.copy(source='test.cfg', dest='running-config')

    def test_copy_abort_n(self):
        self.c.copy(source='somefile.bin', dest='flash:')


class TestMaintenanceMode(unittest.TestCase):

    def test_maintenance_mode_context_manager(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()
        c.settings.MAINTENANCE_MODE_WAIT_TIME = 1
        c.settings.MAINTENANCE_MODE_TIMEOUT = 10
        with c.maintenance_mode() as m:
            output = m.execute('help')
            self.assertEqual(output, 'help')
        c.disconnect()

    def test_switchto_maintenance(self):
        c = Connection(
            hostname='PE1',
            start=['mock_device_cli --os iosxe --state general_enable --hostname PE1'],
            os='iosxe',
            mit=True
        )
        c.connect()
        c.settings.MAINTENANCE_MODE_WAIT_TIME = 1
        c.settings.MAINTENANCE_MODE_TIMEOUT = 10
        c.switchto('maintenance')
        c.switchto('enable')
        c.disconnect()

if __name__ == "__main__":
    unittest.main()
