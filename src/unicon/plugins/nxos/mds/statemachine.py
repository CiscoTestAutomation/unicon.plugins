__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon.plugins.nxos.statemachine import NxosSingleRpStateMachine
from unicon.plugins.nxos.mds.patterns import NxosMdsPatterns
from unicon.statemachine import State, Path

patterns = NxosMdsPatterns()


class NxosMdsSingleRpStateMachine(NxosSingleRpStateMachine):
    def create(self):
        super().create()
        self.remove_path('enable', 'shell')
        self.remove_path('shell', 'enable')
        self.remove_state('shell')

        shell = State('shell', patterns.shell_prompt)
        tie = State('tie', patterns.tie_prompt)
        enable = self.get_state('enable')

        self.add_state(shell)
        self.add_state(tie)

        enable_to_shell = Path(enable, shell, 'bash', None)
        shell_to_enable = Path(shell, enable, 'exit', None)

        enable_to_tie = Path(enable, tie, 'san-ext-tuner', None)
        tie_to_enable = Path(tie, enable, 'end', None)

        # Add State and Path to State Machine
        self.add_path(enable_to_shell)
        self.add_path(shell_to_enable)
        self.add_path(enable_to_tie)
        self.add_path(tie_to_enable)


class NxosMdsDualRpStateMachine(NxosMdsSingleRpStateMachine):

    def create(self):
        super().create()
