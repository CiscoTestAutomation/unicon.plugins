'''
Author: Knox Hutchinson
Contact: https://dataknox.dev
https://twitter.com/data_knox
https://youtube.com/c/dataknox
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.statemachine import Path
from unicon.eal.dialogs import Dialog
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine
from . import statements as stmts


class DellSingleRpStateMachine(GenericSingleRpStateMachine):

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

        self.remove_path('disable', 'enable')
        enable = self.get_state('enable')
        disable = self.get_state('disable')
        disable_to_enable = Path(disable,
                                 enable,
                                 'enable',
                                 Dialog([stmts.password_stmt]))
        self.add_path(disable_to_enable)
