""" State machine for Aci """

__author__ = "dwapstra"

import re

from unicon.core.errors import SubCommandFailure, StateMachineError
from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.generic.statemachine import default_statement_list
from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog, Statement

from .patterns import AciPatterns, AciSetupPatterns

patterns = AciPatterns()
statements = GenericStatements()
setup_patterns = AciSetupPatterns()


class AciStateMachine(StateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)        
        setup = State('setup', list(setup_patterns.__dict__.values()))

        self.add_state(enable)
        self.add_state(config)
        self.add_state(setup)

        enable_to_config = Path(enable, config, 'configure', None)
        config_to_enable = Path(config, enable, 'end', None)

        self.add_path(enable_to_config)
        self.add_path(config_to_enable)

        self.add_default_statements(default_statement_list)
