'''
Connection Statemachine
-----------------------
The connection state machine holds the details of all supported states of a 
given platform, and handles the migration of the device from current state to
any possible next state.
The state machineclass provides a create method where all the device states 
have to be created. State machine should be subclass of StateMachine class 
from unicon.statemachine.
Because this is an imaginary platform we invented from IOSv platform, we can
inherit IOSv implementation as basis.
'''

from unicon.statemachine import Path
from unicon.eal.dialogs import Dialog
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine
from . import statements as stmts


class DellosSingleRpStateMachine(GenericSingleRpStateMachine):

    def create(self):
        '''
        statemachine class's create() method is its entrypoint. This showcases
        how to setup a statemachine in Unicon. 
        '''
        super().create()

        # remove some known path
        self.remove_path('enable', 'rommon')
        self.remove_path('rommon', 'disable')
        self.remove_state('rommon')

        # modify a path by removing it, creating a new one and replacing it
        self.remove_path('disable', 'enable')
        enable = [state for state in self.states if state.name == 'enable'][0]
        disable = [state for state in self.states if state.name == 'disable'][0]
        disable_to_enable = Path(disable,
                                 enable,
                                 'enable',
                                 Dialog([stmts.login_stmt]))
        self.add_path(disable_to_enable)
