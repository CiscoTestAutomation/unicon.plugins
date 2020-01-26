

from .patterns import (AireosReloadPatterns, AireosExecutePatterns)

reload_patterns = AireosReloadPatterns()
execute_patterns = AireosExecutePatterns()


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
        self.press_any_key_stmt = [execute_patterns.press_any_key,
                                   'send( )',
                                   None, True, False]
        self.yes_no_stmt = [execute_patterns.are_you_sure,
                            'sendline(y)',
                            None, True, False]
        self.press_enter_stmt = [execute_patterns.press_enter_stmt,
                                 'sendline()',
                                 None, True, False]
        self.would_you_like_to_save_stmt = [execute_patterns.would_you_like_to_save,
                                 'sendline(y)',
                                 None, True, False]

aireos_statements = AireOsStatements()

reload_statements = [aireos_statements.are_you_sure_stmt,
                     aireos_statements.force_reboot_stmt,
                     aireos_statements.enter_user_name_stmt,  # loop_continue=False
                     aireos_statements.would_you_like_to_save_stmt]  

execute_statements = [aireos_statements.press_any_key_stmt,
                      aireos_statements.yes_no_stmt,
                      aireos_statements.press_enter_stmt]
