__author__ = "dwapstra"

from unicon.eal.dialogs import Statement
from .service_patterns import AciReloadPatterns

pat = AciReloadPatterns()


class AciReloadStatements(object):

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

s = AciReloadStatements()

reload_statement_list = [s.factory_reset,
                         s.restart_proceed,
                         s.press_any_key, # loop_continue=False
                         s.login # loop_continue=False
                        ]

