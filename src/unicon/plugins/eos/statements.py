'''
Author: Richard Day
Contact: https://www.linkedin.com/in/richardday/, https://github.com/rich-day

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import GenericStatements
from .patterns import EOSPatterns
from unicon.bases.routers.connection import ENABLE_CRED_NAME
from unicon.plugins.generic.statements import enable_password_handler

statements = GenericStatements()
patterns = EOSPatterns()

def login_handler(spawn, context, session):
    spawn.sendline(context['enable_password'])

def send_enabler(spawn, context, session):
    spawn.sendline('enable')

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
                        action=enable_password_handler,
                        args=None,
                        loop_continue=True,
                        continue_timer=False)