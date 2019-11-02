
from unicon.eal.dialogs import Dialog

from .patterns import (AireosReloadPatterns,
    AireosPingPatterns, AireosCopyPatterns)

reload_patterns = AireosReloadPatterns()
 

class AireOsStatements():
    """
        Class that defines the Statements for AireOS platform
        implementation
    """
    def __init__(self):
        self.are_you_sure_stmt = [reload_patterns.are_you_sure,
                                  'sendline(y)',
                                  None, True, False]
        self.force_reboot_stmt = [reload_patterns.force_reboot,
                                  'sendline(y)',
                                  None, True, False]
        self.enter_user_name_stmt = [reload_patterns.enter_user_name,
                                    None, None, False, False]


aireos_statements = AireOsStatements()

reload_statements = [aireos_statements.are_you_sure_stmt,
                     aireos_statements.force_reboot_stmt,
                     aireos_statements.enter_user_name_stmt # loop_continue=False
                    ]
