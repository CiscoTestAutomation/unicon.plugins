'''
Connection Settings
-------------------

Connection settings are basically various key/value pairs that controls the
default behavior of a connection. 

'''

from unicon.plugins.generic.settings import GenericSettings


class DnosSettings(GenericSettings):
 
    def __init__(self):
        # inherit any parent settings
        super().__init__()

        # and modify some for our own
        self.CONNECTION_TIMEOUT = 60*3
        self.HA_INIT_EXEC_COMMANDS = []
        self.HA_INIT_CONFIG_COMMANDS = []

        # and we could add more - to be used in plugins if needed
        # self.<keyword> = <value>