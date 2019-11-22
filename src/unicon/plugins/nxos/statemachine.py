from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine
from unicon.plugins.generic.statemachine import GenericDualRpStateMachine
from unicon.plugins.nxos.patterns import NxosPatterns
from unicon.statemachine import State, Path

patterns = NxosPatterns()

class NxosSingleRpStateMachine(GenericSingleRpStateMachine):
    def create(self):
        super().create()
        self.remove_path('disable', 'enable')
        self.remove_path('rommon', 'disable')
        self.remove_path('enable', 'disable')
        self.remove_state('disable')
        # Adding SHELL state to NXOS platform.
        shell = State('shell', patterns.shell_prompt)
        enable = self.get_state('enable')
        # Loader state
        loader = State('loader', patterns.loader_prompt)
        # Guestshell state
        guestshell = State('guestshell', patterns.guestshell_prompt)

        enable_to_shell = Path(enable, shell, 'run bash', None)
        shell_to_enable = Path(shell, enable, 'exit', None)

        enable_to_guestshell = Path(enable, guestshell, 'guestshell', None)
        guestshell_to_enable = Path(guestshell, enable, 'exit', None)

        # Add State and Path to State Machine
        self.add_state(shell)
        self.add_state(loader)
        self.add_state(guestshell)
        self.add_path(enable_to_shell)
        self.add_path(shell_to_enable)
        self.add_path(enable_to_guestshell)
        self.add_path(guestshell_to_enable)

class NxosDualRpStateMachine(GenericDualRpStateMachine):
    def create(self):
        super().create()
        self.remove_state('standby_locked')
        self.remove_path('disable', 'enable')
        self.remove_path('rommon', 'disable')
        self.remove_path('enable', 'disable')
        self.remove_state('disable')
        # Adding SHELL state to NXOS platform.
        shell = State('shell', patterns.shell_prompt)
        enable = self.get_state('enable')
        # Loader state
        loader = State('loader', patterns.loader_prompt)
        # Guestshell state
        guestshell = State('guestshell', patterns.guestshell_prompt)

        enable_to_shell = Path(enable, shell, 'run bash', None)
        shell_to_enable = Path(shell, enable, 'exit', None)

        enable_to_guestshell = Path(enable, guestshell, 'guestshell', None)
        guestshell_to_enable = Path(guestshell, enable, 'exit', None)

        # Add State and Path to State Machine
        self.add_state(shell)
        self.add_state(loader)
        self.add_state(guestshell)
        self.add_path(enable_to_shell)
        self.add_path(shell_to_enable)
        self.add_path(enable_to_guestshell)
        self.add_path(guestshell_to_enable)

