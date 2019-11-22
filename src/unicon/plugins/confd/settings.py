""" Defines the settings for ConfD based unicon connections """

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


from unicon.plugins.generic.settings import GenericSettings


class ConfdSettings(GenericSettings):
    """" Generic platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()
        self.CISCO_INIT_EXEC_COMMANDS = [
            'screen-length 0',
            'screen-width 0',
            'idle-timeout 0'
        ]
        self.CISCO_INIT_CONFIG_COMMANDS = []

        self.JUNIPER_INIT_EXEC_COMMANDS = [
            'set screen length 0',
            'set screen width 0',
            'set idle-timeout 0'
        ]
        self.JUNIPER_INIT_CONFIG_COMMANDS = []

        # Prompt prefixes will be removed from the output by the configure() and execute() services
        self.JUNIPER_PROMPT_PREFIX = "\[edit\]"

        self.ERROR_PATTERN = [
            'Error:',
            'syntax error',
            'Aborted',
            'result false'
        ]

        self.ESCAPE_CHAR_CHATTY_TERM_WAIT = 0.1

        self.IGNORE_CHATTY_TERM_OUTPUT = False

        self.EXEC_ALLOW_STATE_CHANGE = True