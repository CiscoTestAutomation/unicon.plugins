"""
ConfD statements
"""
from unicon.eal.dialogs import Statement
from .patterns import ConfdPatterns


pat = ConfdPatterns()


def console_session(spawn, context):
    context['console'] = True


class ConfdStatements():
    """
        Class that defines the Statements for Confd platform
        implementation
    """
    def __init__(self):
        self.connected_console_stmt = Statement(pattern=pat.connected_console,
                                                action=console_session,
                                                args=None,
                                                loop_continue=True,
                                                continue_timer=False)



confd_statements = ConfdStatements()

confd_statement_list = [confd_statements.connected_console_stmt]

