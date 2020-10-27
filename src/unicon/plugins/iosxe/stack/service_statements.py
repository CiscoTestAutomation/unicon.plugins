""" Generic IOS-XE Stack Service Statements """
import time
from unicon.eal.dialogs import Statement
from unicon.plugins.generic.service_statements import reload_statement_list
from .service_patterns import StackIosXESwitchoverPatterns, StackIosXEReloadPatterns

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

def stack_press_return(spawn, context):
    time.sleep(spawn.timeout)
    spawn.sendline()


# switchover service statements
switchover_pat = StackIosXESwitchoverPatterns()

save_config = Statement(pattern=switchover_pat.save_config,
                        action='sendline(yes)',
                        loop_continue=True, continue_timer=False)
proceed_sw = Statement(pattern=switchover_pat.proceed_switchover,
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
                        loop_continue=True, continue_timer=False)

user_acc = Statement(pattern=switchover_pat.useracess,
                        action=None, args=None,
                        loop_continue=True, continue_timer=False)
switch_prompt = Statement(pattern=switchover_pat.rommon_prompt,
                        action=update_curr_state, args={'state': 'rommon'},
                        loop_continue=False, continue_timer=False)
en_state = Statement(pattern=switchover_pat.enable_prompt,
                        action=update_curr_state, args={'state': 'enable'},
                        loop_continue=False, continue_timer=False)
dis_state = Statement(pattern=switchover_pat.disable_prompt,
                        action=update_curr_state, args={'state': 'disable'},
                        loop_continue=False, continue_timer=False)
press_return = Statement(pattern=switchover_pat.press_return,
                        action=stack_press_return, args=None,
                        loop_continue=True, continue_timer=False)

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
                                en_state, dis_state, press_return, switchover_fail]

# reload service statements
reload_pat = StackIosXEReloadPatterns()

reload_shelf = Statement(pattern=reload_pat.reload_entire_shelf,
                        action='sendline()',
                        loop_continue=True, continue_timer=False)

stack_reload_stmt_list = list(reload_statement_list)

stack_reload_stmt_list.extend([en_state, dis_state])
stack_reload_stmt_list.insert(0, press_return)
stack_reload_stmt_list.insert(0, reload_shelf)

send_boot = Statement(pattern=switchover_pat.rommon_prompt,
                      action=send_boot_cmd, loop_continue=False,
                      continue_timer=False)
