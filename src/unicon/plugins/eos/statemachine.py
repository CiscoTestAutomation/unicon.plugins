'''
Author: Richard Day
Contact: https://www.linkedin.com/in/richardday/, https://github.com/rich-day

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.statemachine import Path
from unicon.eal.dialogs import Dialog
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine
from . import statements as stmts

class EOSSingleRpStateMachine(GenericSingleRpStateMachine):

    def create(self):

        super().create()

        self.remove_path('enable', 'rommon')
        self.remove_path('rommon', 'disable')
        self.remove_state('rommon')

        self.remove_path('disable', 'enable')
        enable = [state for state in self.states if state.name == 'enable'][0]
        disable = [state for state in self.states if state.name == 'disable'][0]
        disable_to_enable = Path(disable, 
                                 enable, 
                                 'enable',
                                 Dialog([stmts.password_stmt]))
        self.add_path(disable_to_enable)
