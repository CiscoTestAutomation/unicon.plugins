__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine
from unicon.plugins.generic.statements import GenericStatements
from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog
from .statements import IosPagentStatements

statements = GenericStatements()
ios_pagent_statements = IosPagentStatements()


class IosPagentSingleRpStateMachine(GenericSingleRpStateMachine):
    def create(self):
        super().create()

        # Overload disable->enable path to account for Pagent key entry
        self.remove_path('disable', 'enable')
        enable = [state for state in self.states if state.name == 'enable'][0]
        disable = [state for state in self.states \
            if state.name == 'disable'][0]
        disable_to_enable = Path(disable, enable, 'enable',
            Dialog([
                statements.password_stmt,
                ios_pagent_statements.pagent_lic_stmt]))
        self.add_path(disable_to_enable)



