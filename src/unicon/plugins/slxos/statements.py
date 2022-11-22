"""
Module:
    unicon.plugins.slxos
Author:
    Fabio Pessoa Nunes (https://www.linkedin.com/in/fpessoanunes/)
Description:
    Module for defining all the Statements and callback required for Slxos
"""

from unicon.eal.dialogs import Statement
from unicon.plugins.slxos.patterns import SlxosPatterns
from unicon.plugins.generic.statements import pre_connection_statement_list, \
                                              login_handler, \
                                              user_access_verification, \
                                              password_handler, \
                                              bad_password_handler, \
                                              incorrect_login_handler


pat = SlxosPatterns()

#############################################################
#  Slxos statements
#############################################################


class SlxosStatements(object):
    """
        Class that defines All the Statements for Slxos platform
        implementation
    """

    def __init__(self):
        '''
         All Slxos Statements
        '''

        self.bad_password_stmt = Statement(pattern=pat.bad_passwords,
                                           action=bad_password_handler,
                                           args=None,
                                           loop_continue=False,
                                           continue_timer=False)
        self.login_incorrect = Statement(pattern=pat.login_incorrect,
                                         action=incorrect_login_handler,
                                         args=None,
                                         loop_continue=True,
                                         continue_timer=False)
        self.login_stmt = Statement(pattern=pat.username,
                                    action=login_handler,
                                    args=None,
                                    loop_continue=True,
                                    continue_timer=False)
        self.useraccess_stmt = Statement(pattern=pat.useracess,
                                         action=user_access_verification,
                                         args=None,
                                         loop_continue=True,
                                         continue_timer=False)
        self.password_stmt = Statement(pattern=pat.password,
                                       action=password_handler,
                                       args=None,
                                       loop_continue=True,
                                       continue_timer=False)
        self.save_confirm = Statement(pattern=pat.save_confirm,
                                      action='sendline(y)',
                                      loop_continue=True,
                                      continue_timer=False)

#############################################################
#  Statement lists
#############################################################


slxos_statements = SlxosStatements()

#############################################################
# Authentication Statements
#############################################################

authentication_statement_list = [slxos_statements.bad_password_stmt,
                                 slxos_statements.login_incorrect,
                                 slxos_statements.login_stmt,
                                 slxos_statements.useraccess_stmt,
                                 slxos_statements.password_stmt
                                 ]

connection_statement_list = authentication_statement_list + \
                            pre_connection_statement_list
