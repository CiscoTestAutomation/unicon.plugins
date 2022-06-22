'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''
from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.aos.patterns import aosPatterns
from unicon.plugins.generic.statements import password_handler

statements = GenericStatements()
patterns = aosPatterns()

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
                       continue_timer=False
                       trim_buffer=True)

enable_stmt = Statement(pattern=patterns.disable_mode,
                        action=send_enabler,
                        args=None,
                        loop_continue=True,
                        continue_timer=False
                        trim_buffer=True)

password_stmt = Statement(pattern=patterns.password,
                          action=password_handler,
                          args=None,
                          loop_continue=True,
                          continue_timer=False
                          trim_buffer=True)

login_password = Statement(pattern=patterns.linePassword,
                           action=line_password_handler,
                           args=None,
                           loop_continue=True,
                           continue_timer=False
                           trim_buffer=True)
