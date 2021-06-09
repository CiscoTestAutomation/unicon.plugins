'''
Author: Sam Johnson
Contact: samuel.johnson@gmail.com
https://github.com/TestingBytes

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.plugins.gaia.statements import GaiaStatements
from unicon.statemachine import Path, State
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine
from .patterns import GaiaPatterns
from unicon.eal.dialogs import Dialog

patterns = GaiaPatterns()
statements = GaiaStatements()


class GaiaStateMachine(GenericSingleRpStateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        '''
        statemachine class's create() method is its entrypoint. This showcases
        how to setup a statemachine in Unicon.
        '''

        clish = State("clish", patterns.clish_prompt)
        expert = State("expert", patterns.expert_prompt)

        self.add_state(clish)
        self.add_state(expert)

        # Assume inital state is 'clish'. If 'expert' is detected by
        # GaiaConnectionProvider.init_handle. These Path commands will
        # be changed at runtime.

        clish_to_expert = Path(clish, expert, 'expert', Dialog([statements.expert_password_stmt]))
        expert_to_clish = Path(expert, clish, 'exit', None)

        self.add_path(clish_to_expert)
        self.add_path(expert_to_clish)
