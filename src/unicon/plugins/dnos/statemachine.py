'''
Connection Statemachine
-----------------------

The connection state machine holds the details of all supported states of a 
given platform, and handles the migration of the device from current state to
any possible next state.

The state machineclass provides a create method where all the device states 
have to be created. State machine should be subclass of StateMachine class 
from unicon.statemachine.
'''

from unicon.statemachine import State, Path, StateMachine
# from unicon.eal.dialogs import Statement, Dialog
from unicon.plugins.dnos.patterns import DnosPatterns


pat = DnosPatterns()


class DnosSingleRpStateMachine(StateMachine):

    def create(self):
        '''
        statemachine class's create() method is its entrypoint. This showcases
        how to setup a statemachine in Unicon. 
        '''
        enable = State('enable', pat.operation_prompt)
        self.add_state(enable)
        # operation = State('operation', pat.operation_prompt)
        # self.add_state(operation)
        # configuration = State('configuration', pat.configuration_prompt)
        # self.add_state(configuration)

        # operation_to_configuration = Path(operation, configuration, 'configure')
        # self.add_path(operation_to_configuration)
        # configuration_to_operation = Path(configuration, operation, 'exit')
        # self.add_path(configuration_to_operation)
        