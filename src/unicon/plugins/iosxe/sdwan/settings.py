
from unicon.plugins.iosxe.settings import IosXESettings

class SDWANSettings(IosXESettings):
    def __init__(self):
        super().__init__()
        self.HA_INIT_EXEC_COMMANDS = [
            'term length 0',
            'term width 0',
            'show sdwan software',
            'show sdwan version',
            'show version'
        ]
        self.HA_INIT_CONFIG_COMMANDS = [
            'no logging console'
        ]
