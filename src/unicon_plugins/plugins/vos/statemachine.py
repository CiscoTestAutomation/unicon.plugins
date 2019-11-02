""" State machine for Uc """

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import re

from unicon.core.errors import SubCommandFailure, StateMachineError
from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog, Statement

from .patterns import VosPatterns
patterns = VosPatterns()

from .statements import vos_default_statement_list


class VosStateMachine(StateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        shell = State('shell', patterns.prompt)
        self.add_state(shell)
        self.add_default_statements(vos_default_statement_list)
