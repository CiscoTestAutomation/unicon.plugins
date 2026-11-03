"""
Unit test for IOS-XE stack config-sync messages printed after the prompt.
"""
import re
import time
import unittest
from unittest.mock import MagicMock

from unicon.plugins.generic.statements import (
    generic_statements, syslog_wait_send_return)


class TestIosXEApplyConfigSyslog(unittest.TestCase):

    def test_apply_config_message_matches_syslog_and_recovers_prompt(self):
        buffer = 'group_ott-c9300#\nApplying config on Switch 3...[DONE]\n'
        last_line = buffer.rstrip().splitlines(keepends=True)[-1]

        pattern = re.compile(generic_statements.syslog_msg_stmt.pattern, re.S)
        self.assertIsNotNone(pattern.search(last_line))

        spawn = MagicMock()
        spawn.buffer = buffer
        spawn.settings.SYSLOG_WAIT = 0
        spawn.settings.SYSLOG_SETTLE_TIMEOUT = 0.01
        spawn.read_update_buffer = MagicMock()
        session = {}

        syslog_wait_send_return(spawn, session)
        spawn.sendline.assert_not_called()

        syslog_wait_send_return(spawn, session)
        spawn.sendline.assert_called_once()


class TestIosXEPnpTimeoutSyslog(unittest.TestCase):

    @staticmethod
    def _matches(message):
        pattern = re.compile(generic_statements.syslog_msg_stmt.pattern, re.S)
        return pattern.search(message) is not None

    def test_pnp_timeout_matches_syslog_and_recovers_prompt(self):
        buffer = (
            '(unlicensed)Router#\r\n'
            'PnP HTTP timed out (5/10) on connection to PnP server '
            '(http://devicehelper-ng.cisco.com.:80/pnp/HELLO)\r\n'
        )
        last_line = buffer.rstrip().splitlines(keepends=True)[-1]

        self.assertTrue(self._matches(last_line))

        spawn = MagicMock()
        spawn.buffer = buffer
        spawn.settings.SYSLOG_WAIT = 0
        spawn.settings.SYSLOG_SETTLE_TIMEOUT = 0.01
        spawn.read_update_buffer = MagicMock()
        spawn.match.match_output = last_line
        session = {}

        syslog_wait_send_return(spawn, session)
        spawn.sendline.assert_called_once()

        syslog_wait_send_return(spawn, session)
        spawn.sendline.assert_called_once()

    def test_pnp_timeout_waits_for_quiet_after_multiple_chunks(self):
        spawn = MagicMock()
        spawn.buffer = (
            '(unlicensed)Router#\r\n'
            'PnP HTTP timed out (5/10) on connection to PnP server '
            '(http://devicehelper-ng.cisco.com.:80/pnp/HELLO)\r\n'
        )
        spawn.settings.SYSLOG_WAIT = 0.005
        spawn.settings.SYSLOG_SETTLE_TIMEOUT = 0.05
        spawn.match.match_output = spawn.buffer
        update_count = 0
        chunks = (
            '%SYS-5-CONFIG_I: Configured from console\r\n',
            '%PNP-6-PNP_DISCOVERY_STARTED: PnP Discovery started\r\n',
            '%PNP-6-PNP_BEST_UDI_UPDATE: Best UDI updated\r\n',
        )

        def read_update_buffer():
            nonlocal update_count
            if update_count < len(chunks):
                spawn.buffer += chunks[update_count]
            update_count += 1
            time.sleep(0.001)

        def sendline():
            spawn.buffer += '(unlicensed)Router#\r\n'

        spawn.read_update_buffer.side_effect = read_update_buffer
        spawn.sendline.side_effect = sendline

        syslog_wait_send_return(spawn, {})

        spawn.sendline.assert_called_once()
        self.assertGreaterEqual(
            spawn.read_update_buffer.call_count,
            len(chunks) + 1,
        )
        self.assertTrue(spawn.buffer.endswith('(unlicensed)Router#\r\n'))

    def test_pnp_timeout_settling_stops_at_overall_deadline(self):
        spawn = MagicMock()
        spawn.buffer = 'PnP HTTP timed out'
        spawn.settings.SYSLOG_WAIT = 0.005
        spawn.settings.SYSLOG_SETTLE_TIMEOUT = 0.015
        spawn.match.match_output = (
            'PnP HTTP timed out on connection to PnP server (192.0.2.1)'
        )

        def read_update_buffer():
            spawn.buffer += 'x'
            time.sleep(0.001)

        spawn.read_update_buffer.side_effect = read_update_buffer

        syslog_wait_send_return(spawn, {})

        spawn.sendline.assert_not_called()
        self.assertGreater(spawn.read_update_buffer.call_count, 1)

    def test_pnp_timeout_match_is_endpoint_independent(self):
        messages = (
            'PnP HTTP timed out (1/3) on connection to PnP server '
            '(https://pnp-lab.example.net:8443/bootstrap)',
            'PnP HTTP timed out on connection to PnP server (192.0.2.1)',
        )

        for message in messages:
            with self.subTest(message=message):
                self.assertTrue(self._matches(message))

    def test_pnp_timeout_match_is_line_anchored(self):
        messages = (
            'command output: PnP HTTP timed out (5/10)',
            'PnP HTTP timeout (5/10)',
            'PnP HTTP timed out while contacting 192.0.2.1',
            'PnP Discovery started',
            'ordinary command output',
        )

        for message in messages:
            with self.subTest(message=message):
                self.assertFalse(self._matches(message))


if __name__ == '__main__':
    unittest.main()
