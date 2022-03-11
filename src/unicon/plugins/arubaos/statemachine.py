'''
Author: Yannick Koehler
Contact: yannick@koehler.name
'''
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine, config_transition
from unicon.statemachine import State, Path
from .patterns import ArubaosPatterns

patterns = ArubaosPatterns()


class ArubaosSingleRpStateMachine(GenericSingleRpStateMachine):
    def create(self):
        """creates the generic state machine"""

        ##########################################################
        # State Definition
        ##########################################################

        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)

        ##########################################################
        # Path Definition
        ##########################################################

        enable_to_config = Path(enable, config, config_transition)
        config_to_enable = Path(config, enable, 'end')

        self.add_state(enable)
        self.add_state(config)

        self.add_path(enable_to_config)
        self.add_path(config_to_enable)
