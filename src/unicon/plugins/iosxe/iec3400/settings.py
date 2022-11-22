

from unicon.plugins.iosxe.settings import IosXESettings


class IosXEIec3400Settings(IosXESettings):

    def __init__(self):
        super().__init__()
        self.RELOAD_TIMEOUT = 120

        self.HA_INIT_EXEC_COMMANDS = []
        self.HA_INIT_CONFIG_COMMANDS = []
