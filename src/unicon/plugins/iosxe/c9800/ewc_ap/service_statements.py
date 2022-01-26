"""Unicon eal Statements and callbacks relevant to the iosxe/c9800/ewc Unicon plugin

Copyright (c) 2019-2020 by cisco Systems, Inc.
All rights reserved.
"""

from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import ssh_continue_connecting
from unicon.plugins.generic.service_statements import send_yes_callback
from .patterns import IosXEEWCBashShellPatterns, IosXEEWCAPShellPatterns


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Bash Shell Statements
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
bash_patterns = IosXEEWCBashShellPatterns()

bash_are_you_sure = Statement(pattern=bash_patterns.coral_are_you_sure,
                              action=send_yes_callback,
                              loop_continue=True,
                              continue_timer=False)

bash_hostname_enable = Statement(pattern=bash_patterns.coral_hostname_enable,
                                 action=None,
                                 loop_continue=False,
                                 continue_timer=False)

enter_bash_shell_statement_list = [
    bash_are_you_sure,
    bash_hostname_enable
]


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# AP Shell Callbacks
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def send_context_ap_enable(spawn, context, session):
    credentials = context.get('credentials', {})
    ap_enable = credentials.get('ap', {}).get('enable_password', 'lab')
    return spawn.sendline(ap_enable)


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# AP Shell Statements
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
ap_patterns = IosXEEWCAPShellPatterns()

ap_are_you_sure = Statement(pattern=ap_patterns.ap_are_you_sure,
                            action=ssh_continue_connecting,
                            loop_continue=True,
                            continue_timer=True)

ap_enable_stmt = Statement(pattern=ap_patterns.password,
                            action=send_context_ap_enable,
                            loop_continue=True,
                            continue_timer=True)


enter_ap_shell_statement_list = [
    ap_are_you_sure,
]
