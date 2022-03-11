'''
Author: Yannick Koehler
Contact: yannick@koehler.name
'''
from unicon.plugins.generic.settings import GenericSettings


class ArubaosSettings(GenericSettings):
    
    def __init__(self):
        super().__init__()
        self.CONNECTION_TIMEOUT = 60
        self.HA_INIT_EXEC_COMMANDS = [
            'no paging'
        ]
        self.HA_INIT_CONFIG_COMMANDS = []
        