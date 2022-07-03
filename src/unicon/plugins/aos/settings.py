'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.plugins.generic import GenericSettings
#This enables logging in the script.
import logging
#Logging disable disables logging in the script. In order to turn on logging, comment out logging disable.
logging.disable(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

from unicon.plugins.generic.settings import GenericSettings

class aosSettings(GenericSettings):
    logging.debug('***Settings aosSettings class called(%s)***')
    def __init__(self):
        logging.debug('***Settings init funtion Loaded(%s)***')
        # inherit any parent settings
        super().__init__()
        self.CONNECTION_TIMEOUT = 60
        self.EXPECT_TIMEOUT = 60
        self.ESCAPE_CHAR_CALLBACK_PRE_SENDLINE_PAUSE_SEC = 3
        self.HA_INIT_EXEC_COMMANDS = []
        self.HA_INIT_CONFIG_COMMANDS = []
        self.CONSOLE_TIMEOUT = 60
        self.ATTACH_CONSOLE_DISABLE_SLEEP = 100
