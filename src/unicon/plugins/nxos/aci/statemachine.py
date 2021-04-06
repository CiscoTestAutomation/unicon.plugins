""" State machine for Aci """

__author__ = "dwapstra"

from unicon.statemachine import State, Path

from ..statemachine import NxosSingleRpStateMachine
from .patterns import AciPatterns

patterns = AciPatterns()


class AciStateMachine(NxosSingleRpStateMachine):

    def create(self):
        super().create()
        enable = self.get_state('enable')
        enable.pattern = patterns.enable_prompt
        boot = State('boot', patterns.loader_prompt)
        module = self.get_state('module')

        self.remove_path(enable, module)

        enable_to_module = Path(enable, module, 'vsh_lc', None)

        self.add_state(boot)

        self.add_path(enable_to_module)
