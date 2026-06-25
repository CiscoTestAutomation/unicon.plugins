"""
Unit test for IOS-XE stack config-sync messages printed after the prompt.
"""
import re
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
        spawn.read_update_buffer = MagicMock()
        session = {}

        syslog_wait_send_return(spawn, session)
        syslog_wait_send_return(spawn, session)

        spawn.sendline.assert_called_once()


if __name__ == '__main__':
    unittest.main()
