
from unicon.statemachine import State, Path
from unicon.eal.dialogs import Statement, Dialog

from unicon.statemachine import State, Path, StateMachine

from .patterns import OnsPatterns

patterns = OnsPatterns()


class OnsSingleRpStateMachine(StateMachine):

    def create(self):
        tl1 = State('tl1', patterns.tl1_prompt)
        self.add_state(tl1)
