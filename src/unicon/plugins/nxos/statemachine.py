from unicon.plugins.generic.statements import default_statement_list
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine
from unicon.plugins.generic.statemachine import GenericDualRpStateMachine
from unicon.plugins.nxos.patterns import NxosPatterns
from unicon.statemachine import State, Path



patterns = NxosPatterns()


class NxosSingleRpStateMachine(GenericSingleRpStateMachine):
    def create(self):
        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)
        shell = State('shell', patterns.shell_prompt)
        loader = State('loader', patterns.loader_prompt)
        guestshell = State('guestshell', patterns.guestshell_prompt)

        enable_to_config = Path(enable, config, 'config term', None)
        config_to_enable = Path(config, enable, 'end', None)

        enable_to_shell = Path(enable, shell, 'run bash', None)
        shell_to_enable = Path(shell, enable, 'exit', None)

        enable_to_guestshell = Path(enable, guestshell, 'guestshell', None)
        guestshell_to_enable = Path(guestshell, enable, 'exit', None)

        # Add State and Path to State Machine
        self.add_state(enable)
        self.add_state(config)
        self.add_state(shell)
        self.add_state(loader)
        self.add_state(guestshell)

        self.add_path(enable_to_config)
        self.add_path(config_to_enable)
        self.add_path(enable_to_shell)
        self.add_path(shell_to_enable)
        self.add_path(enable_to_guestshell)
        self.add_path(guestshell_to_enable)

        self.add_default_statements(default_statement_list)


class NxosDualRpStateMachine(NxosSingleRpStateMachine):
    def create(self):
        super().create()
