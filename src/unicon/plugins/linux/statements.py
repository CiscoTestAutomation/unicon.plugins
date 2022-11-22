from unicon.core.errors import ConnectionError
from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import (pre_connection_statement_list,
                                               generic_statements)
from unicon.plugins.generic.service_statements import (
    execution_statement_list as generic_execution_statements)
from unicon.plugins.utils import (get_current_credential,
                                  common_cred_username_handler,
                                  common_cred_password_handler)

from .patterns import LinuxPatterns

pat = LinuxPatterns()


def username_handler(spawn, context, session):
    credential = get_current_credential(context=context, session=session)
    if credential:
        common_cred_username_handler(spawn=spawn, context=context,
                                     credential=credential)
    else:
        spawn.sendline(context['username'])


def password_handler(spawn, context, session):
    credential = get_current_credential(context=context, session=session)
    if credential:
        common_cred_password_handler(spawn=spawn, context=context,
                                     credential=credential, session=session)
    else:
        spawn.sendline(context['password'])


def custom_auth_username_password_statements(login_pattern=None,
                                             password_pattern=None):
    stmt_list = []
    if login_pattern:
        login_stmt = Statement(pattern=login_pattern,
                               action=username_handler,
                               args=None,
                               loop_continue=True,
                               continue_timer=False)
        stmt_list.append(login_stmt)
    if password_pattern:
        password_stmt = Statement(pattern=password_pattern,
                                  action=password_handler,
                                  args=None,
                                  loop_continue=True,
                                  continue_timer=False)
        stmt_list.append(password_stmt)
    return stmt_list


class LinuxStatements(object):

    def __init__(self):
        self.username_stmt = Statement(pattern=pat.username,
                                       action=username_handler,
                                       args=None,
                                       loop_continue=True,
                                       continue_timer=False)
        self.password_stmt = Statement(pattern=pat.password,
                                       action=password_handler,
                                       args=None,
                                       loop_continue=True,
                                       continue_timer=False)
        self.passphrase_stmt = Statement(pattern=pat.passphrase_prompt,
                                         action=password_handler,
                                         args=None,
                                         loop_continue=True,
                                         continue_timer=False)


linux_statements = LinuxStatements()
linux_pre_connection_statement_list = pre_connection_statement_list
linux_auth_other_statement_list = [generic_statements.login_incorrect]
linux_auth_username_password_statement_list = [linux_statements.username_stmt,
                                               linux_statements.password_stmt,
                                               linux_statements.passphrase_stmt]
linux_execution_statements = generic_execution_statements + [generic_statements.sudo_stmt]
