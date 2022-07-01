'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.aos.statemachine import aosSingleRpStateMachine
from unicon.plugins.aos.services import aosServiceList
from unicon.plugins.aos.settings import aosSettings
from unicon.plugins.aos.connection_provider import aosSingleRpConnectionProvider
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def wait_and_send_yes(spawn):
    logging.debug('init wait and send yes(%s)')
    time.sleep(0.2)
    spawn.sendline('yes')

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

