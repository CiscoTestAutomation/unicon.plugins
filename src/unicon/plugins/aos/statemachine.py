'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson and Cisco Development Team:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Statement, Dialog
from .patterns import aosPatterns
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine, config_transition
import logging
from unicon.plugins.generic.statements import default_statement_list
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class aosSingleRpStateMachine(GenericSingleRpStateMachine):
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
        executive = State('executive', r'.*#$')
        config = State('config', r'.*config.*#$')
        enable = State('enable', r'.*>$')

        ##########################################################
        # Path Definition
        ##########################################################
        enable_to_executive = Path(enable, executive, 'enable', None)
        executive_to_enable = Path(executive, enable, 'exit', None)
        executive_to_config = Path(executive, config, 'configure terminal', None)
        config_to_executive = Path(config, executive, 'exit', None)
        

        # Add State and Path to State Machine
        self.add_state(enable)
        self.add_state(executive)
        self.add_state(config)


        self.add_path(enable_to_executive)
        self.add_path(executive_to_enable)
        self.add_path(executive_to_config)
        self.add_path(config_to_executive)

        #self.add_path(proxy_to_shell)
        #self.add_path(shell_to_proxy)
        self.add_default_statements(default_statement_list)
    def learn_os_state(self):
        logging.debug('***StateMachine aosSingleRpStateMachine learn_os_state function called(%s)***')
        learn_os = State('learn_os', patterns.learn_os_prompt)
        self.add_state(learn_os)
