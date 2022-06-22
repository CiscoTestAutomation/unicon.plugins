'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''
from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.aos.patterns import aosPatterns
from unicon.plugins.generic.statements import enable_password_handler

statements = GenericStatements()
patterns = aosPatterns()

def login_handler(spawn, context, session):
    spawn.sendline(context['\r'])

def send_enabler(spawn, context, session):
    spawn.sendline('\r')


def confirm_imaginary_handler(spawn):
    spawn.sendline('i concur or do i')

# define the list of statements particular to this platform
login_stmt = Statement(pattern=patterns.login_prompt,
                       action=login_handler,
                       args=None,
                       loop_continue=True,
                       continue_timer=False)

enable_stmt = Statement(pattern=patterns.disable_mode,
                        action=send_enabler,
                        args=None,
                        loop_continue=True,
                        continue_timer=False)

password_stmt = Statement(pattern=patterns.password,
                        action=sendline('exit\r'),
                        args=None,
                        loop_continue=True,
                        continue_timer=False)
