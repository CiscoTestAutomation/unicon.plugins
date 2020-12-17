'''
Connection Settings
-------------------
Connection settings are basically various key/value pairs that controls the
default behavior of a connection. 
'''

from unicon.plugins.generic.settings import GenericSettings


class DellosSettings(GenericSettings):

    def __init__(self):
        # inherit any parent settings
        super().__init__()
        self.CONNECTION_TIMEOUT = 60*5
        self.ESCAPE_CHAR_CALLBACK_PRE_SENDLINE_PAUSE_SEC = 1
        self.HA_INIT_EXEC_COMMANDS = [
            'term length 0',
            'show version'
        ]
        self.HA_INIT_CONFIG_COMMANDS = [
            'no logging console'
        ]