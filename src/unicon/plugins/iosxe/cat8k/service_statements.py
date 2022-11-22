__author__ = "Lukas McClelland <lumcclel@cisco.com>"

from unicon.eal.dialogs import Statement
from unicon.plugins.iosxe.cat8k.service_patterns import SwitchoverPatterns, ReloadPatterns
from unicon.plugins.generic.service_statements import (
    save_env, confirm_reset, reload_confirm, reload_confirm_ios)



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
#############################################################################
# Reload Command  Statement
#############################################################################
patterns = ReloadPatterns()

boot_interrupt_stmt = Statement(
    pattern=patterns.boot_interrupt_prompt,
    action='send(\x03)',
    args=None,
    loop_continue=True,
    continue_timer=False)


reload_to_rommon_statement_list = [save_env,
                                   confirm_reset,
                                   reload_confirm,
                                   reload_confirm_ios,
                                   boot_interrupt_stmt]
