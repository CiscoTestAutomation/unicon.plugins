from unicon.plugins.confd.settings import ConfdSettings


class ViptelaSettings(ConfdSettings):
    """" Generic platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()
        self.CISCO_INIT_EXEC_COMMANDS = [
            'screen-length 0',
            'screen-width 256',
            'idle-timeout 0',
            'autowizard false'
        ]
        self.CISCO_INIT_CONFIG_COMMANDS = []

        self.ERROR_PATTERN = [
            'Error:',
            'syntax error',
            'Aborted',
            'result false'
        ]

        self.ESCAPE_CHAR_CHATTY_TERM_WAIT = 0.1

        self.IGNORE_CHATTY_TERM_OUTPUT = True

        self.RELOAD_TIMEOUT = 900
        self.RELOAD_WAIT = 300
        self.RELOAD_RECONNECT_ATTEMPTS = 3
