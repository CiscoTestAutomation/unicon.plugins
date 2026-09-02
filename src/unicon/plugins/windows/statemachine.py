""" State machine for Windows """

__copyright__ = "# Copyright (c) 2018 by cisco Systems, Inc. All rights reserved."
__author__ = "dwapstra"


import re

from unicon.plugins.windows.patterns import WindowsPatterns
from unicon.plugins.generic.statements import GenericStatements

from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog, Statement

from unicon.core.errors import SubCommandFailure, StateMachineError

patterns = WindowsPatterns()
statements = GenericStatements()


class WindowsStateMachine(StateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        shell = State('shell', patterns.prompt)
        self.add_state(shell)
