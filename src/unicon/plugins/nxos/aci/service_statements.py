__author__ = "dwapstra"

from unicon.eal.dialogs import Statement
from .service_patterns import AciN9kReloadPatterns

pat = AciN9kReloadPatterns()


class AciReloadStatements(object):

    def __init__(self):
        self.restart_proceed = Statement(pattern=pat.restart_proceed,
                                          action='sendline(y)',
                                          loop_continue=True,
                                          continue_timer=False)

        self.factory_reset = Statement(pattern=pat.factory_reset,
                                          action='sendline(y)',
                                          loop_continue=True,
                                          continue_timer=False)

        self.login = Statement(pattern=pat.login,
                                  action=None,
                                  args=None,
                                  loop_continue=False,
                                  continue_timer=False)

s = AciReloadStatements()

reload_statement_list = [s.factory_reset,
                         s.restart_proceed,
                         s.login # loop_continue=False
                        ]

