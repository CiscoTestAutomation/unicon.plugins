'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.plugins.generic.settings import GenericSettings


class aosSettings(GenericSettings):

    def __init__(self):
        # inherit any parent settings
        super().__init__()
        self.CONNECTION_TIMEOUT = 10
        self.ESCAPE_CHAR_CALLBACK_PRE_SENDLINE_PAUSE_SEC = 1
        self.HA_INIT_EXEC_COMMANDS = []
        self.HA_INIT_CONFIG_COMMANDS = []