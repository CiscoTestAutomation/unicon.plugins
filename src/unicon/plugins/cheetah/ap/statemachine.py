from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine
from unicon.plugins.generic.statements import GenericStatements, default_statement_list
from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog, Statement
from unicon.plugins.generic.patterns import GenericPatterns

from .patterns import CheetahAPPatterns

statements = GenericStatements()
patterns = CheetahAPPatterns()


class ApSingleRpStateMachine(GenericSingleRpStateMachine):

    def create(self):

        ##########################################################
        # State Definition
        ##########################################################

        disable = State('disable', patterns.disable_prompt)
        enable = State('enable', patterns.enable_prompt)
        shell = State('shell', patterns.ap_shell_prompt)

        ##########################################################
        # Path Definition
        ##########################################################

        disable_to_enable = Path(disable, enable, 'enable', Dialog([
            statements.enable_password_stmt,
            statements.bad_password_stmt,
            statements.syslog_stripper_stmt
        ]))
        enable_to_disable = Path(enable, disable, 'disable', None)

        # Adding SHELL state to Cheetah platform.
        enable_to_shell = Path(enable, shell, 'devshell', None)
        shell_to_enable = Path(shell, enable, 'exit', None)

        # Add State and Path to State Machine
        self.add_state(shell)
        self.add_state(disable)
        self.add_state(enable)

        self.add_path(disable_to_enable)
        self.add_path(enable_to_shell)
        self.add_path(shell_to_enable)
        self.add_path(enable_to_disable)

        self.add_default_statements(default_statement_list)
