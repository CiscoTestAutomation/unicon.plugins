"""
Unit test for selection prompt buried by syslog messages.

When syslog/autoinstall messages appear immediately after the
'Enter your selection [2]:' prompt, the selection pattern must
still match so the correct selection is sent instead of a bare return.
"""
import re
import unittest

from unicon.plugins.generic.patterns import GenericPatterns
from unicon.plugins.generic.statements import generic_statements


class TestSelection(unittest.TestCase):

    def test_selection_pattern_matches(self):
        pat = GenericPatterns()
        selection_re = re.compile(pat.enter_your_selection_2, re.S)
        syslog_re = re.compile(
            generic_statements.syslog_msg_stmt.pattern, re.S)

        buf_normal = (
            '[2] Save this configuration to nvram and exit.\r\n\r\n'
            'Enter your selection [2]: '
        )
        self.assertIsNotNone(selection_re.search(buf_normal))

        buf_buried = (
            'Enter your selection [2]: \r\n'
            'Autoinstall trying DHCPv6 on GigabitEthernet0/0/0\r\n'
        )
        self.assertIsNotNone(selection_re.search(buf_buried),
            'Selection pattern should match when buried by syslog')

        sel_match = selection_re.search(buf_buried)
        syslog_match = syslog_re.search(
            buf_buried.rstrip().splitlines(keepends=True)[-1])
        self.assertIsNotNone(syslog_match,
            'Syslog pattern should also match the last line')
        self.assertIsNotNone(sel_match)

        buf_syslog_only = (
            'Autoinstall trying DHCPv6 on GigabitEthernet0/0/0\r\n'
        )
        self.assertIsNone(selection_re.search(buf_syslog_only))


if __name__ == '__main__':
    unittest.main()
