"""
Module:
    unicon.plugins.linux

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
  This module defines the Linux settings to setup
  the unicon environment required for linux based
  unicon connection
"""
from unicon.plugins.generic.settings import GenericSettings


class LinuxSettings(GenericSettings):
    """" Linux platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()
        self.LINUX_INIT_EXEC_COMMANDS = []

        ## Prompt recovery commands for Linux
        # Default commands: Enter key , Ctrl-C, Enter Key
        self.PROMPT_RECOVERY_COMMANDS = ['\r', '\x03', '\r']

        # Linux plugin uses VT100 terminal to avoid ANSI escape codes in prompt
        # This is seen with linux plugin and causes hostname learning to fail
        # the terminal is set in eal/backend/pty_backend code.
        self.TERM = 'vt100'

        # Environment settings to set before starting connection command
        self.ENV = {
            'TERM': 'vt100',
            'LC_ALL': 'C',  # Setting LC_ALL to C avoids 'LC_ALL: cannot change locale' errors
            # ROWS and COLUMNS will be used to set the terminal size
            'ROWS': 200,
            'COLUMNS': 200
        }

        # Default error pattern
        self.ERROR_PATTERN = [
            r'^.*?No such file or directory\s*$',
            r'^.*?is not in the sudoers file.  This incident will be reported.',
            r'^.*?command not found'
        ]

        # If True, check the command return code for executed commands
        self.CHECK_RETURN_CODE = False
        self.VALID_RETURN_CODES = [0]
