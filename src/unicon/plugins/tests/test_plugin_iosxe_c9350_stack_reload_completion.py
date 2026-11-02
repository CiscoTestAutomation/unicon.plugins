"""Regression test for C9350 members that return to enable at different times."""

import io
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from unicon.plugins.iosxe.cat9k.c9350.stack import service_implementation


class Context(dict):
    def __getattr__(self, name):
        return self[name]


class BootDialog:
    def __init__(self, passes_until_enable):
        self.passes_until_enable = passes_until_enable
        self.calls = {}

    def __iadd__(self, other):
        return self

    def process(self, spawn, timeout, prompt_recovery, context):
        count = self.calls.get(spawn, 0) + 1
        self.calls[spawn] = count
        if count > self.passes_until_enable[spawn]:
            raise AssertionError("Dialog called after the enable prompt")
        if count == self.passes_until_enable[spawn]:
            context['state'] = 'enable'
        return SimpleNamespace(match_output='boot output')


class C9350StackReloadCompletionTest(unittest.TestCase):
    def test_each_member_stops_processing_after_enable_prompt(self):
        peers = []
        for number in (1, 2):
            peer = MagicMock()
            peer.alias = f'peer_{number}'
            peer.context = Context(state='enable')  # stale pre-reload state
            peer.spawn = object()
            peers.append(peer)

        connection = MagicMock()
        connection.active = peers[0]
        connection.subconnections = peers
        connection.settings.STACK_RELOAD_TIMEOUT = 30
        connection.settings.ERROR_PATTERN = []
        connection.settings.POST_RELOAD_WAIT = 0
        connection.settings.RELOAD_POSTCHECK_INTERVAL = 1
        connection.settings.STACK_POST_RELOAD_SLEEP = 0
        connection.settings.LOGIN_PROMPT = None
        connection.settings.PASSWORD_PROMPT = None

        dialog = BootDialog({peers[0].spawn: 2, peers[1].spawn: 3})
        service = object.__new__(service_implementation.C9350StackReload)
        service.connection = connection
        service.context = {}
        service.log_buffer = io.StringIO()
        service.dialog = dialog
        service.reload_command = 'redundancy reload shelf'
        service.prompt_recovery = False
        service.get_service_result = MagicMock()

        with patch.object(service_implementation, 'custom_auth_statements', return_value=[]), \
             patch.object(service_implementation.utils, 'is_active_standby_ready', return_value=True), \
             patch.object(service_implementation, 'sleep'):
            service.call_service(timeout=30)

        self.assertEqual(dialog.calls[peers[0].spawn], 2)
        self.assertEqual(dialog.calls[peers[1].spawn], 3)
        self.assertTrue(service.result)
        connection.disconnect.assert_called_once_with()
        connection.connect.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
