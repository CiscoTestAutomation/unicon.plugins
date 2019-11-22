""" State machine for Staros """

__author__ = "dwapstra"


import re

from unicon.core.errors import SubCommandFailure, StateMachineError
from unicon.plugins.generic.statements import GenericStatements
from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog, Statement

from .patterns import StarosPatterns

patterns = StarosPatterns()
statements = GenericStatements()


class StarosStateMachine(StateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        exec_mode = State('enable', patterns.exec_prompt)
        config_mode = State('config', patterns.config_prompt)

        exec_to_config = Path(exec_mode, config_mode, 'conf', None)
        config_to_exec = Path(config_mode, exec_mode, 'end', None)

        self.add_state(exec_mode)
        self.add_state(config_mode)

        self.add_path(exec_to_config)
        self.add_path(config_to_exec)

