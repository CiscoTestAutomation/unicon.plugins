from unicon.plugins.generic.settings import GenericSettings


class AireosSettings(GenericSettings):
    def __init__(self):
        super().__init__()
        self.EXEC_TIMEOUT = 100
        self.SIZE = 8096
        self.HA_INIT_EXEC_COMMANDS = []
        self.HA_INIT_CONFIG_COMMANDS = [
            'paging disable',
            'sessions timeout 0',
            'serial timeout 0'
        ]
        self.RELOAD_TIMEOUT = 400
        self.ERROR_PATTERN = [
            r'^(%\s*)?Error',
            r'syntax error',
            r'Aborted',
            r'result false',
            r'^This command has been deprecated',
            r'^Incorrect usage.',
            r'^Incorrect input',
            r'^HELP',
            r'^[Ii]nvalid',
            r'^[Ww]arning'
        ]
        self.LOGIN_PROMPT = r'^.*?User:\s*$'
        self.DEFAULT_LEARNED_HOSTNAME = r'(.*?)'
