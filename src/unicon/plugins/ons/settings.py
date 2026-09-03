
from unicon.plugins.generic.settings import GenericSettings

class OnsSettings(GenericSettings):
    def __init__(self):
        super().__init__()
        self.HA_INIT_EXEC_COMMANDS = []
        self.HA_INIT_CONFIG_COMMANDS = []
