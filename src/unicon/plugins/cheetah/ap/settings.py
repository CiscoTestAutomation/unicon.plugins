__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"

from unicon.plugins.generic.settings import GenericSettings


class ApSettings(GenericSettings):
    def __init__(self):
        super().__init__()

        self.HA_INIT_EXEC_COMMANDS = [
            'exec-timeout 0',
            'terminal length 0',
            'terminal width 0',
            'show version',
            'logging console disable',
        ]
