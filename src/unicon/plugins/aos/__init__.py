'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo, Knox Hutchinson and pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com):
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
The order of operations is that the init file is accessed, then the connection_provider file makes the connection using the statements file,
and once the connection is established, the state machine is used. The settings file is where settings can be set. The service implementation file
and services file are where differnt services can be added to this plugin.
'''

from unicon.bases.routers.connection import BaseSingleRpConnection
from .connection_provider import aosSingleRpConnectionProvider
from unicon.plugins.aos.services import aosServiceList
from unicon.plugins.aos.settings import aosSettings
from .statemachine import aosSingleRpStateMachine

#This enables logging in the script.
import logging
#Logging disable disables logging in the script. In order to turn on logging, comment out logging disable.
logging.disable(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

#Checking to see if this is necessary. I will most likely take this out.
def wait_and_send_yes(spawn):
    logging.debug('init wait and send yes(%s)')
    time.sleep(0.2)
    spawn.sendline('yes')

#This is the main class which calls in all of the other files.
class aosSingleRPConnection(BaseSingleRpConnection):
    '''aosSingleRPConnection
    
    This supports logging into an Aruba switch.
    '''
    logging.debug('***init aosSingleRPConnection called(%s)***')
    os = 'aos'
    logging.debug('***init os statement passed(%s)***')
    chassis_type = 'single_rp'
    logging.debug('***init chassis type passed(%s)***')
    state_machine_class = aosSingleRpStateMachine
    logging.debug('***init state machine class loaded(%s)***')
    connection_provider_class = aosSingleRpConnectionProvider
    logging.debug('***init Connection Provider Loaded(%s)***')
    subcommand_list = aosServiceList
    logging.debug('***init Service List Loaded(%s)***')
    settings = aosSettings()
    logging.debug('***init Settings Loaded(%s)***')

