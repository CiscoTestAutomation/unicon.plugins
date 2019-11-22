""" State machine for Fxos """

__author__ = "dwapstra"


from unicon.plugins.generic.statements import GenericStatements
from unicon.core.errors import SubCommandFailure, StateMachineError
from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog, Statement

from .patterns import FxosPatterns

patterns = FxosPatterns()
statements = GenericStatements()


class FxosStateMachine(StateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
      shell = State('shell', patterns.shell_prompt)
      self.add_state(shell)
