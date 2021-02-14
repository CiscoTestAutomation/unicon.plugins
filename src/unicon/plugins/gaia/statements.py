'''
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import GenericStatements
from .patterns import GaiaPatterns 

statements = GenericStatements()
patterns = GaiaPatterns()

def login_handler(spawn, context, session):
    spawn.sendline(context['login'])

def password_handler(spawn, context, session):
    credential = get_current_credential(context=context, session=session)
    if credential:
        common_cred_password_handler(spawn=spawn, context=context, credential=credential)
    else:
        spawn.sendline(context['password'])

# define the list of statements particular to this platform
login_stmt = Statement(pattern=patterns.login_prompt,
                       action=login_handler,
                       args=None,
                       loop_continue=True,
                       continue_timer=False)

password_stmt = Statement(pattern=patterns.password,
                        action=password_handler,
                        args=None,
                        loop_continue=True,
                        continue_timer=False)


