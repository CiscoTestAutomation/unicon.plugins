"""
Module:
    unicon.plugins.slxos
Author:
    Fabio Pessoa Nunes (https://www.linkedin.com/in/fpessoanunes/)
Description:
    This module implements a Slxos state machine which can be used
    by majority of the platforms. It should also be used as starting
    point by further sub classing it.
"""

from unicon.plugins.slxos.patterns import SlxosPatterns
from unicon.statemachine import State, Path, StateMachine

patterns = SlxosPatterns()


class SlxosSingleRpStateMachine(StateMachine):

    """
        Defines Slxos StateMachine for singleRP
        Statemachine keeps in track all the supported states
        for this platform, also have detail about moving from
        one state to another
    """

    def create(self):
        """creates the slxos state machine"""

        ##########################################################
        # State Definition
        ##########################################################
        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)

        ##########################################################
        # Path Definition
        ##########################################################
        enable_to_config = Path(enable, config, 'configure', None)
        config_to_enable = Path(config, enable, 'exit', None)

        # Add State and Path to State Machine
        self.add_state(enable)
        self.add_state(config)

        self.add_path(enable_to_config)
        self.add_path(config_to_enable)
