import unittest
from unittest.mock import Mock, patch

import unicon
from unicon import Connection
from unicon.plugins.iosxe.cat9kv import (
    IosXECat9kvServiceList,
    IosXECat9kvSingleRpConnection,
)
from unicon.plugins.iosxe.cat9kv.service_implementation import Reload
from unicon.plugins.iosxe.cat9kv.statemachine import \
    IosXECat9kvSingleRpStateMachine
from unicon.plugins.iosxe.cat9kv.statements import (
    boot_from_rommon,
    send_escape,
    settings,
)
from unicon.plugins.iosxe.service_implementation import Reload as IosxeReload

unicon.settings.Settings.POST_DISCONNECT_WAIT_SEC = 0
unicon.settings.Settings.GRACEFUL_DISCONNECT_WAIT_SEC = 0.2


class TestIosXECat9KvPlugin(unittest.TestCase):

    def test_plugin_resolution(self):
        d = Connection(
            hostname='switch',
            start=['mock_device_cli --os iosxe --state c8kv_rommon --hostname switch'],
            os='iosxe',
            platform='cat9kv',
            model='cat9kv',
            log_buffer=True)
        self.assertTrue(
            d.__class__.__module__.endswith('plugins.iosxe.cat9kv'))
        self.assertEqual(d.platform, 'cat9kv')

    def test_connection_uses_cat9kv_state_machine(self):
        self.assertIs(
            IosXECat9kvSingleRpConnection.state_machine_class,
            IosXECat9kvSingleRpStateMachine)

    def test_rommon_to_disable_path_supports_grub(self):
        d = Connection(
            hostname='switch',
            start=['mock_device_cli --os iosxe --state c8kv_exec --hostname switch'],
            os='iosxe',
            platform='cat9kv',
            model='cat9kv',
            log_buffer=True)

        rommon = d.state_machine.get_state('rommon')
        path = d.state_machine.get_path('rommon', 'disable')
        self.assertIsNotNone(path)
        self.assertIn('grub', rommon.pattern)


class TestIosXECat9KvPluginBootStatements(unittest.TestCase):

    def test_boot_from_rommon_with_grub_boot_image_sends_escape(self):
        statemachine = Mock()
        spawn = Mock()
        context = {'grub_boot_image': 'GOLDEN IMAGE'}

        with patch('unicon.plugins.iosxe.cat9kv.statements.logger.info') as log_info:
            boot_from_rommon(statemachine, spawn, context)

        log_info.assert_any_call('Using grub_boot_image: GOLDEN IMAGE')
        spawn.send.assert_called_once_with('\x1b')
        spawn.sendline.assert_not_called()
        self.assertIn('boot_start_time', context)
        self.assertEqual(context['boot_prompt_count'], 1)

    def test_send_escape_raises_after_max_attempts(self):
        spawn = Mock()
        session = {'boot_attempt_count': settings.MAX_BOOT_ATTEMPTS}
        with self.assertRaisesRegex(Exception, 'Too many failed boot attempts'):
            send_escape(spawn, session)
        spawn.send.assert_not_called()


class TestIosXECat9KvPluginReload(unittest.TestCase):

    def test_service_list_uses_cat9kv_reload(self):
        service_list = IosXECat9kvServiceList()
        self.assertIs(service_list.reload, Reload)
        self.assertTrue(issubclass(service_list.reload, IosxeReload))


if __name__ == '__main__':
    unittest.main()
