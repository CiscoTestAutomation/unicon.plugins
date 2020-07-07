# Python
from time import sleep

#Unicon
from unicon.eal.dialogs import Statement
from .service_patterns import IOSXRSwitchoverPatterns
from unicon.plugins.iosxr.patterns import IOSXRPatterns


def commit_retry(spawn, context, session):
    '''
        A method to resend `commit` command when fails
        during lock down on the configuration session
    '''
    sleep_time = context['settings'].COMMIT_RETRY_SLEEP
    commit_retries = context['settings'].COMMIT_RETRIES

    for retry in range(commit_retries):
        # Loop over the commit process as per the number of commit retries
        try:
            sleep(sleep_time)
            spawn.sendline('commit')
            # Thu Jun 11 16:37:38.005 UTC
            spawn.expect(r'^.*[a-zA-Z]+ +[a-zA-Z]+ +[0-9]+ +[\d\:\.]+ +[A-Z]+.*')
        except:
            # Configuration session is still in lock
            continue

        # Commit went through successfully
        break

    # Empty buffer
    spawn.sendline('')
    spawn.expect(r'')


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

commit_retry_stmt = Statement(pattern=pat.commit_retry,
                              action=commit_retry,
                              args=None,
                              loop_continue=True,
                              continue_timer=False)

commit_verified = Statement(pattern=pat.commit_verified,
                              action=commit_retry,
                              args=None,
                              loop_continue=True,
                              continue_timer=False)

switchover_statement_list = [prompt_switchover_stmt,
                             rp_in_standby_stmt # loop_continue = False
                             ]

config_commit_stmt_list = [commit_changes_stmt,
                           commit_replace_stmt,
                           confirm_y_prompt_stmt,
                           commit_retry_stmt,
                           commit_verified]

execution_statement_list = [commit_replace_stmt,
                            confirm_y_prompt_stmt]

