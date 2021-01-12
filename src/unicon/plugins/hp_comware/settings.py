'''
Author: Renato Almeida de Oliveira
Contact: renato.almeida.oliveira@gmail.com
https://twitter.com/ORenato_Almeida
https://www.youtube.com/c/RenatoAlmeidadeOliveira
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.plugins.generic.settings import GenericSettings


class HPSettings(GenericSettings):

    def __init__(self):
        # inherit any parent settings
        super().__init__()
        self.CONNECTION_TIMEOUT = 60*5
        self.ESCAPE_CHAR_CALLBACK_PRE_SENDLINE_PAUSE_SEC = 1
        self.HA_INIT_EXEC_COMMANDS = ['screen-length disable']
        self.HA_INIT_CONFIG_COMMANDS = []