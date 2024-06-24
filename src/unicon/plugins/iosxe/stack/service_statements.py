""" Generic IOS-XE Stack Service Statements """
from time import time, sleep
from datetime import datetime, timedelta
from unicon.eal.dialogs import Statement

from unicon.plugins.generic.service_statements import reload_statement_list
from unicon.plugins.generic.statements import buffer_settled
from unicon.plugins.iosxe.service_statements import factory_reset_confirm, are_you_sure_confirm
from .service_patterns import StackIosXESwitchoverPatterns, StackIosXEReloadPatterns
from .exception import StackMemberReadyException


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

def stack_press_return(spawn, context, session):
    # for stack devices if we reload from a member console we will see 2 press return to continue.
    # to make sure that we get out of the process dialog when all the members are ready we 
    # make sure first we match "All switches in the stack have been discovered. Accelerating discovery" in the
    # buffer then we raise the StackMemberReadyException to end the process.
    if session.get('apply_config_on_all_members') or session.get('bp_console'):
        spawn.log.info('Waiting for buffer to settle')
        timeout_time = context.get('post_reload_wait_time', 60)
        if not isinstance(timeout_time, timedelta):
            timeout_time = timedelta(seconds=timeout_time)
        start_time = current_time = datetime.now()
        while (current_time - start_time) < timeout_time:
            if buffer_settled(spawn, wait_time=15):
                spawn.log.info('Buffer settled, accessing device..')
                break
            current_time = datetime.now()
            if (current_time - start_time) > timeout_time:
                spawn.log.info('Time out, trying to access device..')
                break
        spawn.sendline()
        raise StackMemberReadyException

def apply_config_on_all_switch(spawn, session):
    # we need to match theis pattern to make sure all the members are ready and we can access the device
    """ Handles the number of apply configure message seen after install image """
    session["apply_config_on_all_members"] = True

def bp_console_handler(spawn, session):
    ''' strack_press_return will not wait for session["apply_config_on_all_members"] to be set
        However, this pattern "All switches in the stack have been discovered. Accelerating discovery"
        will never be seen for new stack design, which will cause the stack_press_return to wait forever.
        Therefore, also checking bp-console prompt to make sure the reload process dialog will stop.'''
    session["bp_console"] = True


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

press_return_stack = Statement(pattern=switchover_pat.press_return,
                         action=stack_press_return,
                         args=None,
                         loop_continue=True,
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
                              found_return, switchover_fail]

# reload service statements
reload_pat = StackIosXEReloadPatterns()

reload_shelf = Statement(pattern=reload_pat.reload_entire_shelf,
                         action='sendline()',
                         loop_continue=True,
                         continue_timer=False)

reload_fast = Statement(pattern=reload_pat.reload_fast,
                         action='sendline()',
                         loop_continue=True,
                         continue_timer=False)

apply_config = Statement(pattern=reload_pat.apply_config,
                         action=apply_config_on_all_switch,
                         loop_continue=True,
                         continue_timer=False)


bp_console = Statement(pattern=reload_pat.bp_console,
                          action=bp_console_handler,
                          loop_continue=True,
                          continue_timer=False)

stack_reload_stmt_list = list(reload_statement_list)

stack_reload_stmt_list.extend([en_state, dis_state])
stack_reload_stmt_list.insert(0, press_return_stack)
stack_reload_stmt_list.insert(0, reload_shelf)
stack_reload_stmt_list.insert(0, reload_fast)
stack_reload_stmt_list.insert(0, apply_config)
stack_reload_stmt_list.insert(0, bp_console)


stack_factory_reset_stmt_list = [factory_reset_confirm, are_you_sure_confirm]

send_boot = Statement(pattern=switchover_pat.rommon_prompt,
                      action=send_boot_cmd, loop_continue=False,
                      continue_timer=False)
