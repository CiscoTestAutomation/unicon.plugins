""" State machine for Cimc """

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import re

from unicon.plugins.cimc.patterns import CimcPatterns

from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog, Statement

from unicon.core.errors import SubCommandFailure, StateMachineError

from .statements import CimcStatements

patterns = CimcPatterns()
statements = CimcStatements()

default_statement_list = [statements.more_prompt_stmt]


class CimcStateMachine(StateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        shell = State('shell', patterns.prompt)
        self.add_state(shell)
        self.add_default_statements(default_statement_list)
