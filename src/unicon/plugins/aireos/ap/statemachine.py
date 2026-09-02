from unicon.eal.dialogs import Dialog
from unicon.statemachine import Path, State, StateMachine
from unicon.plugins.generic.patterns import GenericPatterns
from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.generic.statements import default_statement_list, authentication_statement_list

statements = GenericStatements()

patterns = GenericPatterns()


class AireosAPStateMachine(StateMachine):
    def create(self):

        disable = State('disable', patterns.disable_prompt)
        enable = State('enable', patterns.enable_prompt)

        self.add_state(enable)
        self.add_state(disable)

        enable_to_disable = Path(enable, disable, 'disable', None)
        disable_to_enable = Path(disable, enable, 'enable',
                                 Dialog([statements.enable_password_stmt, statements.bad_password_stmt]))

        self.add_path(disable_to_enable)
        self.add_path(enable_to_disable)

        self.add_default_statements(default_statement_list)
