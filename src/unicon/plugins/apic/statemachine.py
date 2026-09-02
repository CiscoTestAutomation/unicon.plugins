""" State machine for APIC """

__author__ = "dwapstra"

from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.generic.statemachine import default_statement_list
from unicon.statemachine import State, Path, StateMachine

from .patterns import ApicPatterns, ApicSetupPatterns

patterns = ApicPatterns()
statements = GenericStatements()
setup_patterns = ApicSetupPatterns()


class AciStateMachine(StateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)
        shell = State('shell', patterns.shell_prompt)
        learn_hostname = State('learn_hostname', patterns.learn_hostname)
        setup = State('setup', list(setup_patterns.__dict__.values()))

        self.add_state(enable)
        self.add_state(config)
        self.add_state(learn_hostname)
        self.add_state(setup)
        self.add_state(shell)

        self.add_path(Path(learn_hostname, enable, None, None))
        enable_to_config = Path(enable, config, 'configure', None)
        config_to_enable = Path(config, enable, 'end', None)

        self.add_path(enable_to_config)
        self.add_path(config_to_enable)

        self.add_default_statements(default_statement_list)
