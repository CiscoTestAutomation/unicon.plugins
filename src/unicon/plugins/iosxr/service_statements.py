#Unicon
from unicon.eal.dialogs import Statement
from .service_patterns import (IOSXRSwitchoverPatterns,
                               IOSXRReloadPatterns)
from unicon.plugins.iosxr.patterns import IOSXRPatterns
from unicon.plugins.iosxr.statements import handle_failed_config, switchover_disallowed_handler

pat = IOSXRSwitchoverPatterns()


prompt_switchover_stmt = Statement(pattern=pat.prompt_switchover,
                                   action='sendline()',
                                   args=None,
                                   loop_continue=True,
                                   continue_timer=True)

rp_in_standby_stmt = Statement(pattern=pat.rp_in_standby,
                               action=None,
                               args=None,
                               loop_continue=False,
                               continue_timer=False)
switchover_disallowed_stmt = Statement(pattern=pat.switchover_disallowed,
                               action=switchover_disallowed_handler,
                               args={'error': "Switchover disallowed"},
                               loop_continue=False,
                               continue_timer=False)

# Statements for commit, commit replace commands executed on xr.
pat = IOSXRPatterns()
commit_changes_stmt = Statement(pattern=pat.commit_changes_prompt,
                                action='sendline(yes)',
                                args=None, loop_continue=True,
                                continue_timer=False)

commit_replace_stmt = Statement(pattern=pat.commit_replace_prompt,
                                action='sendline(yes)',
                                args=None,
                                loop_continue=True,
                                continue_timer=False)

confirm_y_prompt_stmt = Statement(pattern=pat.confirm_y_prompt,
                                  action='sendline(y)',
                                  args=None,
                                  loop_continue=True,
                                  continue_timer=False)

failed_config_statement = Statement(pattern=pat.configuration_failed_message,
                                    action=handle_failed_config,
                                    args={'abort': False},
                                    loop_continue=True,
                                    continue_timer=False)

pat = IOSXRReloadPatterns()
confirm_module_reload_stmt = Statement(pattern=pat.reload_module_prompt,
                                       action='sendline(yes)',
                                       args=None,
                                       loop_continue=True,
                                       continue_timer=False)

wish_continue_statement = Statement(pattern=pat.wish_continue,
                                    action='sendline(y)',
                                    args=None,
                                    loop_continue=True,
                                    continue_timer=False)

switchover_statement_list = [prompt_switchover_stmt,
                             rp_in_standby_stmt,  # loop_continue = False
                             switchover_disallowed_stmt
                             ]

config_commit_stmt_list = [commit_changes_stmt,
                           commit_replace_stmt,
                           confirm_y_prompt_stmt]

execution_statement_list = [commit_replace_stmt,
                            confirm_y_prompt_stmt]

reload_statement_list = [confirm_module_reload_stmt,
                         wish_continue_statement]

configure_statement_list = [failed_config_statement]
