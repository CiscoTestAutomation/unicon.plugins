from unicon.plugins.generic.settings import GenericSettings


class AireosAPSettings(GenericSettings):
    def __init__(self):
        super().__init__()
        self.HA_INIT_EXEC_COMMANDS = [
            'terminal length 0',
            'terminal width 0',
            'exec-timeout 0 0',
            'logging console disable'
        ]
        self.HA_INIT_CONFIG_COMMANDS = []

        self.ERROR_PATTERN = [
           r'^%\s*[Ii]nvalid input detected',
           r'^%\s*[Ii]ncomplete'
        ]
