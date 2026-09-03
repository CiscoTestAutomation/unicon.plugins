""" Generic IOS-XE Stack Service Statements """
import re
from datetime import datetime, timedelta

from unicon.eal.dialogs import Statement

from unicon.plugins.generic.service_statements import (reload_statement_list,
                                                       save_env,
                                                       reload_confirm_ios,
                                                       reload_confirm_iosxe,
                                                       reload_entire_shelf,
                                                       reload_this_shelf,
                                                       press_enter,
                                                       press_return)

from unicon.plugins.iosxe.service_statements import (factory_reset_confirm,
                                                     are_you_sure_confirm)
from .service_patterns import (StackIosXESwitchoverPatterns,
                               StackIosXEReloadPatterns)


def update_curr_state(spawn, context, state):
    context['state'] = state


def switchover_failed(spawn, context):
    context['switchover_failed'] = True


def boot_from_rommon(sm, spawn, context):
    cmd = "boot {}".format(context['image_to_boot']) \
        if "image_to_boot" in context else "boot"
    spawn.sendline(cmd)


def send_boot_cmd(spawn, context):
    cmd = "boot {}".format(context['image_to_boot']) \
        if "image_to_boot" in context else "boot"
    spawn.sendline(cmd)


# switchover service statements
switchover_pat = StackIosXESwitchoverPatterns()

save_config = Statement(pattern=switchover_pat.save_config,
                        action='sendline(yes)',
                        loop_continue=True, continue_timer=False)

proceed_sw = Statement(pattern=switchover_pat.switchover_proceed,
                       action='sendline()',
                       loop_continue=True, continue_timer=False)

commit_changes = Statement(pattern=switchover_pat.cisco_commit_changes_prompt,
                           action='sendline(yes)',
                           loop_continue=True, continue_timer=False)

term_state = Statement(pattern=switchover_pat.terminal_state,
                       action='sendline(\r)',
                       loop_continue=True, continue_timer=False)

gen_rsh_key = Statement(pattern=switchover_pat.gen_rsh_key,
                        action='sendline()',
                        loop_continue=True, continue_timer=False)

auto_pro = Statement(pattern=switchover_pat.auto_provision,
                     action='sendline(yes)',
                     loop_continue=True, continue_timer=False)

secure_passwd = Statement(pattern=switchover_pat.secure_passwd_std,
                          action='sendline(no)',
                          loop_continue=True, continue_timer=False)

build_config = Statement(pattern=switchover_pat.build_config,
                         action=None,
                         loop_continue=True, continue_timer=False)

sw_init = Statement(pattern=switchover_pat.switchover_init,
                    action=None,
                    loop_continue=True,
                    continue_timer=False)

user_acc = Statement(pattern=switchover_pat.useracess,
                     action=None,
                     args=None,
                     loop_continue=True,
                     continue_timer=False)

switch_prompt = Statement(pattern=switchover_pat.rommon_prompt,
                          action=update_curr_state,
                          args={'state': 'rommon'},
                          loop_continue=False,
                          continue_timer=False)
fastreload_iosxeswitch = Statement(pattern=switchover_pat.fastreload_iosxeswitch,
                        action='sendline()',
                        loop_continue=True, continue_timer=False)

en_state = Statement(pattern=switchover_pat.enable_prompt,
                     action=update_curr_state,
                     args={'state': 'enable'},
                     loop_continue=False,
                     continue_timer=False)

dis_state = Statement(pattern=switchover_pat.disable_prompt,
                      action=update_curr_state,
                      args={'state': 'disable'},
                      loop_continue=False,
                      continue_timer=False)

found_return = Statement(pattern=switchover_pat.press_return,
                         args=None,
                         loop_continue=False,
                         continue_timer=False)

switchover_fail_pattern = '|'.join([switchover_pat.switchover_fail1,
                                    switchover_pat.switchover_fail2,
                                    switchover_pat.switchover_fail3,
                                    switchover_pat.switchover_fail4,
                                    switchover_pat.switchover_fail5])

switchover_fail = Statement(pattern=switchover_fail_pattern,
                            action=switchover_failed, args=None,
                            loop_continue=False, continue_timer=False)

stack_switchover_stmt_list = [save_config, proceed_sw, commit_changes,
                              term_state, gen_rsh_key, auto_pro, secure_passwd,
                              build_config, sw_init, user_acc, switch_prompt,
                              found_return, switchover_fail, dis_state]
# reload service statements
reload_pat = StackIosXEReloadPatterns()


def stack_wait_and_enter(spawn, wait=0.5):
    """Handle the stack reload ``Press RETURN``/authentication prompt race."""
    last_match = getattr(getattr(spawn, 'match', None), 'last_match', None)
    match_start = last_match.start() if last_match is not None else 0

    wait_time = timedelta(seconds=wait)
    settle_time = current_time = datetime.now()
    while (current_time - settle_time) < wait_time:
        spawn.read_update_buffer()
        current_time = datetime.now()

    settings = getattr(spawn, 'settings', None)
    auth_patterns = (
        reload_pat.username,
        reload_pat.password,
        getattr(settings, 'LOGIN_PROMPT', None),
        getattr(settings, 'PASSWORD_PROMPT', None),
    )
    pending_output = (spawn.buffer or '')[match_start:]
    if any(pattern and re.search(pattern, pending_output, re.DOTALL)
           for pattern in auth_patterns):
        spawn.log.debug(
            'Authentication prompt appeared while waiting; skipping RETURN')
        return

    spawn.sendline()


stack_press_return = Statement(
    pattern=reload_pat.press_return,
    action=stack_wait_and_enter,
    loop_continue=True,
    continue_timer=False,
)

reload_shelf = Statement(pattern=reload_pat.reload_entire_shelf,
                         action='sendline()',
                         loop_continue=True,
                         continue_timer=False)

reload_fast = Statement(pattern=reload_pat.reload_fast,
                        action='sendline()',
                        loop_continue=True,
                        continue_timer=False)

accelarating_discovery = Statement(pattern=reload_pat.accelarating_discovery,
                                   action=None,
                                   args=None,
                                   loop_continue=False,
                                   continue_timer=False)

proceed_prompt_stmt = Statement(pattern=reload_pat.proceed_prompt,
                                   action='sendline(y)',
                                   args=None,
                                   loop_continue=True,
                                   continue_timer=False)

stack_reload_stmt_list_1 = [save_env, reload_confirm_ios, reload_confirm_iosxe,
                            reload_entire_shelf, reload_this_shelf,
                            # Below statements have loop_continue=False
                            # enable and disable state is needed by dialog
                            # processor during member reload to process the
                            # device state during reload
                            en_state, dis_state,
                            switch_prompt,
                            accelarating_discovery, fastreload_iosxeswitch,
                            proceed_prompt_stmt]

# Some stack variants process each "Press RETURN" in separate dialog calls.
stack_reload_stmt_list = list(reload_statement_list)

# The enable and disable states are needed when using `reload slot N`
stack_reload_stmt_list.extend([en_state, dis_state])
stack_reload_stmt_list.insert(0, reload_shelf)
stack_reload_stmt_list.insert(0, reload_fast)

# Both generic statements match "Press RETURN". Keep one stack handler active
# so authentication prompts that arrive while settling stay in this dialog.
stack_reload_auth_stmt_list = [
    stack_press_return if statement is press_enter else statement
    for statement in stack_reload_stmt_list
    if statement is not press_return
]


stack_factory_reset_stmt_list = [factory_reset_confirm, are_you_sure_confirm]

send_boot = Statement(pattern=switchover_pat.rommon_prompt,
                      action=send_boot_cmd, loop_continue=False,
                      continue_timer=False)
