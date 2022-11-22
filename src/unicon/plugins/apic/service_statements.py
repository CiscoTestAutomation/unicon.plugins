__author__ = "dwapstra"

from unicon.eal.dialogs import Statement
from unicon.plugins.generic.service_statements import connection_closed

from .service_patterns import ApicReloadPatterns


pat = ApicReloadPatterns()


class ApicReloadStatements(object):
    def __init__(self):
        self.restart_proceed = Statement(pattern=pat.restart_proceed,
                                         action='sendline(y)',
                                         loop_continue=True,
                                         continue_timer=False)

        self.factory_reset = Statement(pattern=pat.factory_reset,
                                       action='sendline(Y)',
                                       loop_continue=True,
                                       continue_timer=False)

        self.press_any_key = Statement(pattern=pat.press_any_key,
                                       action=None,
                                       args=None,
                                       loop_continue=False,
                                       continue_timer=False)

        self.login = Statement(pattern=pat.login,
                               action=None,
                               args=None,
                               loop_continue=False,
                               continue_timer=False)



apic_stmts = ApicReloadStatements()

reload_statement_list = [apic_stmts.factory_reset,
                         apic_stmts.restart_proceed,
                         apic_stmts.press_any_key,  # loop_continue=False
                         apic_stmts.login,  # loop_continue=False
                         connection_closed  # loop_continue=False
                        ]
