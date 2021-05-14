'''
Author: Sam Johnson
Contact: samuel.johnson@gmail.com
https://github.com/TestingBytes

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.plugins.generic.settings import GenericSettings


class GaiaSettings(GenericSettings):

    def __init__(self):
        # inherit any parent settings
        super().__init__()
        self.CONNECTION_TIMEOUT = 300
        self.ESCAPE_CHAR_CALLBACK_PRE_SENDLINE_PAUSE_SEC = 1
        self.HA_INIT_EXEC_COMMANDS = ['set clienv rows 0']
        self.HA_INIT_CONFIG_COMMANDS = []

        self.ERROR_PATTERN = [
            r'^.*?command not found.*$',
            r'^.*?[Ii]nvalid command.*$'
        ]
