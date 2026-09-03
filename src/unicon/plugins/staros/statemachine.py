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


def quit_monitor(state_machine, spawn, context):
    spawn.send('q')


def send_escape(state_machine, spawn, context):
    spawn.send('\x1b')


class StarosStateMachine(StateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        exec_mode = State('enable', patterns.exec_prompt)
        config_mode = State('config', patterns.config_prompt)
        monitor_mode = State('monitor', patterns.monitor_main_prompt)
        monitor_sub_mode = State('monitor_sub', patterns.monitor_sub_prompt)

        exec_to_config = Path(exec_mode, config_mode, 'conf', None)
        config_to_exec = Path(config_mode, exec_mode, 'end', None)
        monitor_to_exec = Path(monitor_mode, exec_mode, quit_monitor, None)
        monitor_sub_to_monitor = Path(monitor_sub_mode, monitor_mode, send_escape, None)

        self.add_state(exec_mode)
        self.add_state(config_mode)
        self.add_state(monitor_mode)
        self.add_state(monitor_sub_mode)

        self.add_path(exec_to_config)
        self.add_path(config_to_exec)
        self.add_path(monitor_to_exec)
        self.add_path(monitor_sub_to_monitor)
