"""
CIMC statements
"""
from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import GenericStatements


from .patterns import CimcPatterns
pat = CimcPatterns()

class CimcStatements(GenericStatements):
    """
        Class that defines the Statements for CIMC platform
        implementation
    """

    def __init__(self):
        '''
         All CIMC Statements
        '''
        super().__init__()
        self.enter_yes_or_no_stmt = Statement(pattern=pat.enter_yes_or_no,
                                              action='sendline(yes)',
                                              args=None,
                                              loop_continue=True,
                                              continue_timer=False)

