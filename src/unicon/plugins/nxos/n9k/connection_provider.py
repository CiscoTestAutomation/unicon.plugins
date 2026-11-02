from copy import copy

from unicon.plugins.generic.statements import generic_statements
from unicon.plugins.nxos.connection_provider import (
    NxosSingleRpConnectionProvider, NxosDualRpConnectionProvider)
from unicon.plugins.nxos.service_statements import (
    admin_password, secure_password)
from .service_statements import (
    admin_password_setup_stmt, secure_password_setup_stmt,
    setup_syslog_stmt)


def prioritize_setup_password_prompts(base_dialog, custom_statement_count):
    # A boot syslog and the admin password prompt may arrive in the same read
    # as the secure-password question. Keep user connect_reply handlers first.
    statements = base_dialog.statements
    for offset, (setup_statement, n9k_statement) in enumerate((
            (secure_password, secure_password_setup_stmt),
            (admin_password, admin_password_setup_stmt))):
        index = next(i for i in range(len(statements) - 1, -1, -1)
                     if statements[i].pattern == setup_statement.pattern and
                     statements[i].action is setup_statement.action and
                     statements[i].args == setup_statement.args)
        statements.pop(index)
        statements.insert(custom_statement_count + offset,
                          copy(n9k_statement))
    # Standalone syslogs still need the generic Return to recover the prompt.
    # Only syslogs between setup questions are stripped without a Return.
    syslog = generic_statements.syslog_msg_stmt
    for index, statement in enumerate(statements):
        if (statement.pattern == syslog.pattern and
                statement.action is syslog.action):
            statements[index] = copy(setup_syslog_stmt)
            break
    return base_dialog


class Nxos9kSingleRpConnectionProvider(NxosSingleRpConnectionProvider):

    def get_connection_dialog(self):
        return prioritize_setup_password_prompts(
            super().get_connection_dialog(),
            len(self.connection.connect_reply.statements))


class Nxos9kDualRpConnectionProvider(NxosDualRpConnectionProvider):

    def get_connection_dialog(self):
        return prioritize_setup_password_prompts(
            super().get_connection_dialog(),
            len(self.connection.connect_reply.statements))
