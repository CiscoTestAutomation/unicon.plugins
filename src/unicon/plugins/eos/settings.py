'''
Author: Richard Day
Contact: https://www.linkedin.com/in/richardday/, https://github.com/rich-day

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.plugins.generic.settings import GenericSettings

class EOSSettings(GenericSettings):
 
    def __init__(self):
        super().__init__()
        self.CONNECTION_TIMEOUT = 60*5
        self.HA_INIT_CONFIG_COMMANDS = [
            'no logging console'
        ]