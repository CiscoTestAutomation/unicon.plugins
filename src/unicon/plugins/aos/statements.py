'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''
from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.aos.patterns import aosPatterns
from unicon.plugins.generic.statements import pre_connection_statement_list
from unicon.plugins.generic.statements import password_handler
from unicon.plugins.generic.statements import login_handler
from unicon.plugins.generic.statements import enable_password_handler
from unicon.eal.helpers import sendline
statements = GenericStatements()
patterns = aosPatterns()

class aosStatements(object):
    def __init__(self):

# This is the statements to login to AOS.
        self.login_stmt = Statement(pattern=patterns.login_prompt,
                                action=login_handler,
                                args=None,
                                loop_continue=True,
                                continue_timer=False)

        self.password_stmt = Statement(pattern=patterns.password,
                                action=enable_password_handler,
                                args=None,
                                loop_continue=True,
                                continue_timer=False)

#############################################################
#  Statement lists
#############################################################

aos_statements = aosStatements()

#############################################################
# Authentication Statements
#############################################################

aosAuthentication_statement_list = [aos_statements.login_stmt,
                                 aos_statements.password_stmt]

aosConnection_statement_list = aosAuthentication_statement_list + pre_connection_statement_list
