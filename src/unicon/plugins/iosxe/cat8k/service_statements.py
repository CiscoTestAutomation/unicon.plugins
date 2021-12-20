__author__ = "Lukas McClelland <lumcclel@cisco.com>"

from unicon.eal.dialogs import Statement
from unicon.plugins.iosxe.cat8k.service_patterns import SwitchoverPatterns


#############################################################################
# Switchover Command  Statement
#############################################################################
pat = SwitchoverPatterns()

save_config = Statement(pattern=pat.save_config,
                        action='sendline(yes)',
                        loop_continue=True,
                        continue_timer=True)

build_config = Statement(pattern=pat.build_config,
                         action=None,
                         args=None,
                         loop_continue=True,
                         continue_timer=True)

prompt_switchover = Statement(pattern=pat.prompt_switchover,
                              action='sendline()',
                              loop_continue=True,
                              continue_timer=True)

switchover_complete = Statement(pattern=pat.switchover_complete,
                                action='sendline()',
                                loop_continue=False,
                                continue_timer=False)

switchover_statement_list = [save_config,
                             build_config,
                             prompt_switchover,
                             switchover_complete]