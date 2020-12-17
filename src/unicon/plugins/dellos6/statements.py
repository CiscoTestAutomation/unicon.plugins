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
from unicon.plugins.generic.statements import GenericStatements
from .patterns import DellosPatterns as patterns

# handlers are necessary actions to take (functions)
# when a particular statement is met

statements = GenericStatements()


def login_handler(spawn, context, session):
    spawn.sendline(context['enable_password'])


def confirm_imaginary_handler(spawn):
    spawn.sendline('i concur')


# define the list of statements particular to this platform
login_stmt = Statement(pattern=patterns.login_prompt,
                       action=login_handler,
                       args=None,
                       loop_continue=True,
                       continue_timer=False)

confirm_imaginary_platform = Statement(pattern=patterns.confirm_imaginary,
                                       action=confirm_imaginary_handler,
                                       args=None,
                                       loop_continue=True,
                                       continue_timer=False)
