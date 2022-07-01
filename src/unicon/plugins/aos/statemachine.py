'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson and Cisco Development Team:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Statement, Dialog
from unicon.plugins.aos.patterns import aosPatterns
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
patterns = aosPatterns()

class aosSingleRpStateMachine(StateMachine):
    logging.debug('***StateMachine aosSingleRpStateMachine class loaded(%s)***')
    def create(self):
        '''
        statemachine class's create() method is its entrypoint. This showcases
        how to setup a statemachine in Unicon. 
        '''
        logging.debug('***StateMachine aosSingleRpStateMachine create funtion called(%s)***')

        ##########################################################
        # State Definition
        ##########################################################
        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)


        ##########################################################
        # Path Definition
        ##########################################################
        enable_to_config = Path(enable, config, 'configure terminal', None)
        config_to_enable = Path(config, enable, 'exit', None)
        

        # Add State and Path to State Machine
        self.add_state(enable)
        self.add_state(config)
        self.add_path(enable_to_config)
        self.add_path(config_to_enable)

        #self.add_path(proxy_to_shell)
        #self.add_path(shell_to_proxy)
    
    def learn_os_state(self):
        logging.debug('***StateMachine aosSingleRpStateMachine learn_os_state function called(%s)***')
        learn_os = State('learn_os', patterns.learn_os_prompt)
        self.add_state(learn_os)
