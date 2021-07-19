__author__ = 'Difu Hu <pyats-support@cisco.com;pyats-support-ext@cisco.com>'

from unicon.core.errors import ConnectionError
from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import pre_connection_statement_list
from unicon.plugins.utils import (get_current_credential,
                                  common_cred_username_handler,
                                  common_cred_password_handler)

from .patterns import SrosPatterns

pat = SrosPatterns()


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


def permission_denied(spawn):
    raise ConnectionError('Permission denied for device {}'.format(spawn))


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


class SrosStatements(object):

    def __init__(self):
        self.permission_denied_stmt = Statement(pattern=pat.permission_denied,
                                                action=permission_denied,
                                                args=None,
                                                loop_continue=False,
                                                continue_timer=False)
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
        self.discard_uncommitted = Statement(pattern=pat.discard_uncommitted,
                                             action='sendline(y)',
                                             args=None,
                                             loop_continue=True,
                                             continue_timer=False)


sros_statements = SrosStatements()
sros_pre_connection_statement_list = pre_connection_statement_list
sros_auth_other_statement_list = [sros_statements.permission_denied_stmt]
sros_auth_username_password_statement_list = [sros_statements.username_stmt,
                                              sros_statements.password_stmt]
