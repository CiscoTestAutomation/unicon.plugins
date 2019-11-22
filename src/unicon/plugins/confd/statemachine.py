""" State machine for ConfD """

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import re

from unicon.plugins.confd.patterns import ConfdPatterns
from unicon.plugins.generic.statements import GenericStatements

from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog, Statement

from unicon.core.errors import SubCommandFailure, StateMachineError

patterns = ConfdPatterns()
statements = GenericStatements()

default_statement_list = [statements.more_prompt_stmt]


class ConfdStateMachine(StateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        cisco_exec = State('cisco_exec', patterns.cisco_prompt)
        juniper_exec = State('juniper_exec', patterns.juniper_prompt)
        cisco_config = State('cisco_config', patterns.cisco_config_prompt)
        juniper_config = State('juniper_config', patterns.juniper_config_prompt)

        self.add_state(cisco_exec)
        self.add_state(juniper_exec)
        self.add_state(cisco_config)
        self.add_state(juniper_config)

        cisco_to_juniper_exec = Path(cisco_exec, juniper_exec, 'switch cli', None)
        juniper_to_cisco_exec = Path(juniper_exec, cisco_exec, 'switch cli', None)

        cisco_exec_to_juniper_config = Path(cisco_config, juniper_config, 'switch cli', None)
        juniper_exec_to_cisco_config = Path(juniper_config, cisco_config, 'switch cli', None)

        cisco_exec_to_config = Path(cisco_exec, cisco_config, 'config', None)
        juniper_exec_to_config = Path(juniper_exec, juniper_config, 'configure', None)

        # Ignore config changes on state change
        # config commits are done as part of the configure method
        cisco_config_dialog = Dialog([
            # Uncommitted changes found, commit them? [yes/no/CANCEL] no
            [patterns.cisco_commit_changes_prompt, 'sendline(no)', None, True, False],
            ])
        juniper_config_dialog = Dialog([
            # Discard changes and continue? [yes,no] yes
            [patterns.juniper_commit_changes_prompt, 'sendline(yes)', None, True, False],
            ])

        cisco_config_to_exec = Path(cisco_config, cisco_exec, 'end', cisco_config_dialog)
        juniper_config_to_exec = Path(juniper_config, juniper_exec, 'exit', juniper_config_dialog)

        self.add_path(cisco_to_juniper_exec)
        self.add_path(juniper_to_cisco_exec)
        self.add_path(cisco_exec_to_juniper_config)
        self.add_path(juniper_exec_to_cisco_config)
        self.add_path(cisco_exec_to_config)
        self.add_path(juniper_exec_to_config)
        self.add_path(cisco_config_to_exec)
        self.add_path(juniper_config_to_exec)
        self.add_default_statements(default_statement_list)

    @property
    def current_cli_style(self):
        self.current_state_tokens = self.current_state.split('_')
        if len(self.current_state_tokens) < 1:
            raise StateMachineError('Invalid state')
        style = self.current_state_tokens[0]
        return style

    @property
    def current_cli_mode(self):
        self.current_state_tokens = self.current_state.split('_')
        if len(self.current_state_tokens) < 1:
            raise StateMachineError('Invalid state')
        mode = self.current_state_tokens[1]
        return mode

