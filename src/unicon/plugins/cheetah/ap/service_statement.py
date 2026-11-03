"""
Module:
    unicon.plugins.generic
Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)
Description:
    Module for defining all Services Statement, handlers(callback) and Statement
    list for service dialog would be defined here.
"""

from time import sleep

from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import chatty_term_wait
from unicon.plugins.generic.service_statements import (
    data_pattern as generic_data_pattern,
    extended_ping_dialog_list,
    ping_handler,
    reload_statement_list,
    sweep_range as generic_sweep_range,
)

from .service_patterns import APReloadPatterns, PingPatterns

pat = APReloadPatterns()
ping_pat = PingPatterns()


def send_response(spawn, response=""):
    chatty_term_wait(spawn)
    spawn.sendline(response)


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Reload  Statements
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

ap_shell_prompt = Statement(pattern=pat.ap_shell_prompt,
                            action=send_response, args={'response': '\r'},
                            loop_continue=True,
                            continue_timer=False)

ap_reload_list = list(reload_statement_list)
ap_reload_list.insert(0, ap_shell_prompt)


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Ping Statements
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

# Data pattern [0xABCD]: 0x
ap_data_pattern = Statement(pattern=ping_pat.data_pattern,
                            action=ping_handler,
                            args={'send_key': 'data_pat'},
                            loop_continue=True,
                            continue_timer=False)

# Sweep range of sizes [n]:
ap_sweep_range = Statement(pattern=ping_pat.range,
                           action='sendline()',
                           loop_continue=True,
                           continue_timer=False)

ap_extended_ping_dialog_list = list(extended_ping_dialog_list)
data_pattern_index = ap_extended_ping_dialog_list.index(generic_data_pattern)
ap_extended_ping_dialog_list[data_pattern_index] = ap_data_pattern
sweep_range_index = ap_extended_ping_dialog_list.index(generic_sweep_range)
ap_extended_ping_dialog_list[sweep_range_index] = ap_sweep_range
