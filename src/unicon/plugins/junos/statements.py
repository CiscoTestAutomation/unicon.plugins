"""
Module:
    unicon.plugins.junos

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    Module for defining all the Statements and callback required for the
    Current implementation
"""
from unicon.eal.dialogs import Statement
from unicon.eal.helpers import sendline
from unicon.core.errors import UniconAuthenticationError
from unicon.plugins.junos.patterns import JunosPatterns
from unicon.plugins.generic.statements import pre_connection_statement_list, \
                                              login_handler, user_access_verification, \
                                              password_handler, bad_password_handler, \
                                              incorrect_login_handler


pat = JunosPatterns()

#############################################################
#  Junos statements
#############################################################

class JunosStatements(object):
    """
        Class that defines All the Statements for Junos platform
        implementation
    """

    def __init__(self):
        '''
         All junos Statements
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


#############################################################
#  Statement lists
#############################################################

junos_statements = JunosStatements()

#############################################################
# Authentication Statements
#############################################################

authentication_statement_list = [junos_statements.bad_password_stmt,
                                 junos_statements.login_incorrect,
                                 junos_statements.login_stmt,
                                 junos_statements.useraccess_stmt,
                                 junos_statements.password_stmt
                                 ]

connection_statement_list = authentication_statement_list + pre_connection_statement_list
