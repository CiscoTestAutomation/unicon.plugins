""" IOS-XE Quad State Machine """
from unicon.statemachine import State
from unicon.plugins.iosxe.statemachine import IosXEDualRpStateMachine

from .patterns import IosXEQuadPatterns

patterns = IosXEQuadPatterns()

class IosXEQuadStateMachine(IosXEDualRpStateMachine):

    def create(self):
        super().create()

        # Add RPR state
        rpr = State('rpr', patterns.rpr_state)
        self.add_state(rpr)
