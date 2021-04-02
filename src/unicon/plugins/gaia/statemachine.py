'''
Author: Sam Johnson
Contact: samuel.johnson@gmail.com
https://github.com/TestingBytes

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.statemachine import Path, State, StateMachine
from .patterns import GaiaPatterns

patterns = GaiaPatterns()

class GaiaStateMachine(StateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        '''
        statemachine class's create() method is its entrypoint. This showcases
        how to setup a statemachine in Unicon. 
        '''
        
        # Note: the checkpoint shell 'clish' is implemented as 'enable'
        # Expert mode is not a currently supported state.

        clish = State("enable", patterns.clish_prompt)
        
        self.add_state(clish)     