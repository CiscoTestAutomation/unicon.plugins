"""
Unit tests for SVL designate_handles logic.
"""

import unittest
from unittest.mock import MagicMock

from unicon.plugins.iosxe.cat9k.stackwise_virtual.connection_provider import (
    SHOW_SWITCH_MATCHED_RETRIES,
    SHOW_SWITCH_MATCHED_RETRY_SLEEP,
    StackwiseVirtualConnectionProvider,
)


class TestIosxeSVLDesignateHandles(unittest.TestCase):

    def test_svl_designate_handles_9500(self):
        con = MagicMock()
        con.settings.BOOT_TIMEOUT = 1
        con.settings.EXEC_TIMEOUT = 1
        con.device = MagicMock()
        show_switch_output = "show switch output"
        con.device.execute.return_value = show_switch_output
        con.device.parse.return_value = {
            'switch': {
                'stack': {
                    '1': {'role': 'active'},
                    '2': {'role': 'standby'}
                }
            }
        }

        redundancy_output = "my state = 8  -STANDBY HOT \n"
        show_redundancy_cmd = "show redundancy states"
        redundancy_state_pattern = r"my state = (.*?)\s*$"

        subcon_a = MagicMock()
        subcon_a.alias = 'a'
        subcon_a.state_machine.current_state = 'enable'
        subcon_a.spawn.expect.return_value.match_output = redundancy_output
        subcon_a.spawn.settings.SHOW_REDUNDANCY_CMD = show_redundancy_cmd
        subcon_a.spawn.settings.REDUNDANCY_STATE_PATTERN = redundancy_state_pattern

        subcon_b = MagicMock()
        subcon_b.alias = 'b'
        subcon_b.state_machine.current_state = 'enable'
        subcon_b.spawn.expect.return_value.match_output = redundancy_output
        subcon_b.spawn.settings.SHOW_REDUNDANCY_CMD = show_redundancy_cmd
        subcon_b.spawn.settings.REDUNDANCY_STATE_PATTERN = redundancy_state_pattern

        con._subconnections = {'a': subcon_a, 'b': subcon_b}
        con.subconnections = [subcon_a, subcon_b]
        con._set_active_alias = MagicMock()
        con._set_standby_alias = MagicMock()

        provider = StackwiseVirtualConnectionProvider(con)
        provider.designate_handles()

        con.device.execute.assert_called_once_with(
            "show switch",
            matched_retries=SHOW_SWITCH_MATCHED_RETRIES,
            matched_retry_sleep=SHOW_SWITCH_MATCHED_RETRY_SLEEP,
        )
        con.device.parse.assert_called_once_with(
            "show switch",
            output=show_switch_output,
        )
        subcon_a.spawn.sendline.assert_called_with(show_redundancy_cmd)
        self.assertEqual(con._set_active_alias.call_args_list[-1].args[0], 'b')
        self.assertEqual(con._set_standby_alias.call_args_list[-1].args[0], 'a')


if __name__ == "__main__":
    unittest.main()
