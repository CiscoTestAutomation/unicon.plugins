'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''
from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import GenericStatements
from .patterns import aosPatterns
from unicon.plugins.generic.statements import password_handler

statements = GenericStatements()
patterns = aosPatterns()
patterns = pat

def login_handler(spawn, context, session):
    spawn.sendline(context['\r'])

def send_enabler(spawn, context, session):
    spawn.sendline('\r')

def line_password_handler(spawn, context, session):
    credential = get_current_credential(context=context, session=session)
    if credential:
        common_cred_password_handler(
            spawn=spawn, context=context, credential=credential,
            session=session)
    else:
        spawn.sendline(context['password'])

def confirm_imaginary_handler(spawn):
    spawn.sendline('i concur or do i')

# define the list of statements particular to this platform
login_stmt = Statement(pattern=patterns.login_prompt,
                       action=login_handler,
                       args=None,
                       loop_continue=True,
                       continue_timer=True,
                       trim_buffer=True)

enable_stmt = Statement(pattern=patterns.disable_mode,
                        action=send_enabler,
                        args=None,
                        loop_continue=True,
                        continue_timer=True,
                        trim_buffer=True)

password_stmt = Statement(pattern=patterns.password,
                          action=password_handler,
                          args=None,
                          loop_continue=True,
                          continue_timer=True,
                          trim_buffer=True)

escape_char_stmt = Statement(pattern=patterns.escape_char,
                             action=escape_char_callback,
                             args=None,
                             loop_continue=True,
                             continue_timer=False)
press_return_stmt = Statement(pattern=patterns.press_return,
                              action=wait_and_enter, 
                              args=None,
                              loop_continue=True,
                              continue_timer=False)
connection_refused_stmt = \
    Statement(pattern=patterns.connection_refused,
              action=connection_refused_handler,
              args=None,
              loop_continue=False,
              continue_timer=False)
bad_password_stmt = Statement(pattern=patterns.bad_passwords,
                              action=bad_password_handler,
                              args=None,
                              loop_continue=False,
                              continue_timer=False)

login_incorrect = Statement(pattern=patterns.login_incorrect,
                            action=incorrect_login_handler,
                            args=None,
                            loop_continue=True,
                            continue_timer=False)

disconnect_error_stmt = Statement(pattern=patterns.disconnect_message,
                                  action=connection_failure_handler,
                                  args=None,
                                  loop_continue=False,
                                  continue_timer=False)
useraccess_stmt = Statement(pattern=patterns.useracess,
                                 action=user_access_verification,
                                 args=None,
                                 loop_continue=True,
                                 continue_timer=False)
password_stmt = Statement(pattern=patterns.password,
                          action=password_handler,
                          args=None,
                          loop_continue=True,
                          continue_timer=False)
enable_password_stmt = Statement(pattern=patterns.password,
                                 action=enable_password_handler,
                                 args=None,
                                 loop_continue=True,
                                 continue_timer=False)
enable_secret_stmt = Statement(pattern=patterns.enable_secret,
                               action=enable_password_handler,
                               args=None,
                               loop_continue=True,
                               continue_timer=False)
password_ok_stmt = Statement(pattern=patterns.password_ok,
                             action=sendline,
                             args=None,
                             loop_continue=True,
                             continue_timer=False)
more_prompt_stmt = Statement(pattern=patterns.more_prompt,
                             action=more_prompt_handler,
                             args=None,
                             loop_continue=True,
                             continue_timer=False)
confirm_prompt_stmt = Statement(pattern=patterns.confirm_prompt,
                                action=sendline,
                                args=None,
                                loop_continue=True,
                                continue_timer=False)
confirm_prompt_y_n_stmt = Statement(pattern=patterns.confirm_prompt_y_n,
                                    action='sendline(y)',
                                    args=None,
                                    loop_continue=True,
                                    continue_timer=False)
yes_no_stmt = Statement(pattern=patterns.yes_no_prompt,
                        action=sendline,
                        args={'command': 'y'},
                        loop_continue=True,
                        continue_timer=False)

continue_connect_stmt = Statement(pattern=patterns.continue_connect,
                                  action=ssh_continue_connecting,
                                  args=None,
                                  loop_continue=True,
                                  continue_timer=False)

hit_enter_stmt = Statement(pattern=patterns.hit_enter,
                           action=wait_and_enter,
                           args=None,
                           loop_continue=True,
                           continue_timer=False)

press_ctrlx_stmt = Statement(pattern=patterns.press_ctrlx,
                             action=wait_and_enter,
                             args=None,
                             loop_continue=True,
                             continue_timer=False)

init_conf_stmt = Statement(pattern=patterns.setup_dialog,
                           action='sendline(no)',
                           args=None,
                           loop_continue=True,
                           continue_timer=False)

mgmt_setup_stmt = Statement(pattern=patterns.enter_basic_mgmt_setup,
                            action='send(\x03)',  # Ctrl-C
                            args=None,
                            loop_continue=True,
                            continue_timer=False)

clear_kerberos_no_realm = Statement(pattern=patterns.kerberos_no_realm,
                                    action=sendline,
                                    args=None,
                                    loop_continue=True,
                                    continue_timer=False)

connected_stmt = Statement(pattern=patterns.connected,
                           action=sendline,
                           args=None,
                           loop_continue=True,
                           continue_timer=False)

passphrase_stmt = Statement(pattern=patterns.passphrase_prompt,
                            action=passphrase_handler,
                            args=None,
                            loop_continue=True,
                            continue_timer=False)

sudo_stmt = Statement(pattern=patterns.sudo_password_prompt,
                      action=sudo_password_handler,
                      args=None,
                      loop_continue=True,
                      continue_timer=False)

syslog_msg_stmt = Statement(pattern=patterns.syslog_message_pattern,
                            action=syslog_wait_send_return,
                            args=None,
                            loop_continue=True,
                            trim_buffer=False,
                            continue_timer=False)

syslog_stripper_stmt = Statement(pattern=patterns.syslog_message_pattern,
                                 action=syslog_stripper,
                                 args=None,
                                 loop_continue=True,
                                 trim_buffer=False,
                                 continue_timer=False)

enter_your_selection_stmt = Statement(pattern=patterns.enter_your_selection_2,
                                      action='sendline(2)',
                                      args=None,
                                      loop_continue=True,
                                      continue_timer=True)

press_any_key_stmt = Statement(pattern=patterns.press_any_key,
                               action='sendline()',
                               args=None,
                               loop_continue=True,
                               continue_timer=False)

permission_denied_stmt = Statement(pattern=patterns.permission_denied,
                                   action=permission_denied_handler,
                                   args=None,
                                   loop_continue=False,
                                   continue_timer=False)

terminal_position_stmt = Statement(pattern=patterns.get_cursor_position,
                                   action=terminal_position_handler,
                                   args=None,
                                   loop_continue=True,
                                   continue_timer=False)
