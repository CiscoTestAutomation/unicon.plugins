from typing import Pattern
from unicon.plugins.iosxe.statemachine import IosXEDualRpStateMachine
from .patterns import IosXECat4kPatterns
from unicon.statemachine import State, Path
from unicon.eal.dialogs import Dialog

patterns = IosXECat4kPatterns()


class IosXEC4t3kDualRpStateMachine(IosXEDualRpStateMachine):
    def create(self):
        super().create()

        stby_lock = State('stby_locked', '' )
        self.add_state(stby_lock)