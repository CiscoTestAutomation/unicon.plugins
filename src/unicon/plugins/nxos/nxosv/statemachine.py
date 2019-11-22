__author__ = "Myles Dear <mdear@cisco.com>"

from ..statemachine import NxosSingleRpStateMachine
from unicon.plugins.generic.statements import GenericStatements
from unicon.statemachine import State, Path, StateMachine
from .patterns import NxosPatterns

patterns = NxosPatterns()


class NxosvSingleRpStateMachine(NxosSingleRpStateMachine):
    def create(self):
        super().create()
        enable = self.get_state('enable')

        # Add relaxed prompt to ensure connection succeeds when device
        # is coming up.
        # Saw the following line in the nxosv log:
        # switch# 2016 Sep 28 18:37:47 switch %PLATFORM-2-MOD_DETECT: Module 3 detected (Serial number TM0024CC3FD) Module-Type NX-OSv Ethernet Module Model N7K-F248XP-25
        enable.add_state_pattern(patterns.enable_prompt)
