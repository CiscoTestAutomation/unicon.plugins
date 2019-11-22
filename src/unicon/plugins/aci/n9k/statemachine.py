""" State machine for Aci """

__author__ = "dwapstra"

import re

from unicon.core.errors import SubCommandFailure, StateMachineError
from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.generic.statemachine import default_statement_list
from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog, Statement

from .patterns import AciPatterns

patterns = AciPatterns()
statements = GenericStatements()



class AciStateMachine(StateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        enable = State('enable', patterns.enable_prompt)
        boot = State('boot', patterns.loader_prompt)

        self.add_state(enable)
        self.add_state(boot)
        self.add_default_statements(default_statement_list)
