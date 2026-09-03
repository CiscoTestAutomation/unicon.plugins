"""
Module:
    unicon.plugins.hvrp
Authors:
    Miguel Botia (mibotiaf@cisco.com), Leonardo Anez (leoanez@cisco.com)
Description:
     This module implements a HVRP state machine.
"""

from unicon.plugins.hvrp.patterns import HvrpPatterns
from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog

from unicon.plugins.hvrp.statements import default_statement_list

patterns = HvrpPatterns()


class HvrpSingleRpStateMachine(StateMachine):

    """
        Defines Hvrp StateMachine for singleRP
        Statemachine keeps in track all the supported states
        for this platform, also have detail about moving from
        one state to another
    """


    def create(self):
        """creates the hvrp state machine"""

        ##########################################################
        # State Definition
        ##########################################################
        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)

        """creates the hvrp Paths machine"""
        ##########################################################
        # Path Definition
        ##########################################################
        config_dialog = Dialog([
           [patterns.commit_changes_prompt, 'sendline(yes)', None, True, False],
        ])

        enable_to_config = Path(enable, config, 'system-view', None)
        config_to_enable = Path(config, enable, 'return', config_dialog)


        # Add State and Path to State Machine
        self.add_state(enable)
        self.add_state(config)

        self.add_path(enable_to_config)
        self.add_path(config_to_enable)
        self.add_default_statements(default_statement_list)
