from unicon.plugins.generic.settings import GenericSettings

class NxosSettings(GenericSettings):

    def __init__(self):
        super().__init__()
        self.HA_INIT_EXEC_COMMANDS = [
            'term length 0',
            'term width 511',
            'terminal session-timeout 0'
        ]
        self.HA_INIT_CONFIG_COMMANDS = [
            'no logging console',
            'line console',
            'exec-timeout 0',
            'terminal width 511'
        ]
        self.SWITCHOVER_TIMEOUT = 700
        self.SWITCHOVER_COUNTER = 50
        self.HA_RELOAD_TIMEOUT = 700
        self.RELOAD_TIMEOUT = 400
        self.CONSOLE_TIMEOUT = 30
        self.GUESTSHELL_RETRIES = 20
        self.GUESTSHELL_RETRY_SLEEP = 5
        self.ATTACH_CONSOLE_DISABLE_SLEEP = 250
        self.ERROR_PATTERN = [
            r'^%\s*[Ii]nvalid (command|input)',
            r'^%\s*[Ii]ncomplete (command|input)',
            r'^%\s*[Aa]mbiguous (command|input)'
        ]
