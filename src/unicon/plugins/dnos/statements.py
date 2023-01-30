'''
Connection Statements
---------------------

Automation is all about automatically performing actions without human 
intervention. This includes automatically answering to dialog prompts by 
programmatically replying to each dialog prompt.

Statements are the building blocks of dialog handling logic within Unicon.
Typically Unicon plugins have a statements.py file where all statements 
particular to this platform is located.
'''

from unicon.eal.dialogs import Statement
from unicon.eal.helpers import sendline
from unicon.core.errors import UniconAuthenticationError
from unicon.plugins.generic.statements import pre_connection_statement_list, \
                                              login_handler, user_access_verification, \
                                              password_handler, bad_password_handler, \
                                              incorrect_login_handler
from unicon.plugins.dnos.patterns import DnosPatterns


pat = DnosPatterns()


# define the list of statements particular to this platform
operation_stmt = Statement(pattern=pat.operation_prompt,
                       action=login_handler,
                       args=None,
                       loop_continue=True,
                       continue_timer=False)

