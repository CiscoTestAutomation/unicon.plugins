from unicon.plugins.asa.settings import ASASettings

class ASAvSettings(ASASettings):
    def __init__(self):
        super().__init__()
        self.CONNECTION_TIMEOUT = 300
