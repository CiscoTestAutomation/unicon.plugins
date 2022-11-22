"""
Module:
    unicon.plugins.junos

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:

    This module implements a Junos state machine which can be used
    by majority of the platforms. It should also be used as starting
    point by further sub classing it.
"""
from unicon.plugins.junos.patterns import JunosPatterns
from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Statement, Dialog

patterns = JunosPatterns()


class JunosSingleRpStateMachine(StateMachine):

    """
        Defines Junos StateMachine for singleRP
        Statemachine keeps in track all the supported states
        for this platform, also have detail about moving from
        one state to another
    """

    def create(self):
        """creates the junos state machine"""

        ##########################################################
        # State Definition
        ##########################################################
        shell = State('shell', patterns.shell_prompt)
        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)

        ##########################################################
        # Path Definition
        ##########################################################
        config_dialog = Dialog([
           [patterns.commit_changes_prompt, 'sendline(yes)', None, True, False],
        ])
        enable_to_shell = Path(enable, shell, 'exit', None)
        shell_to_enable = Path(shell, enable, 'cli', None)

        enable_to_config = Path(enable, config, 'configure', None)
        config_to_enable = Path(config, enable, 'exit', config_dialog)

        # Add State and Path to State Machine
        self.add_state(shell)
        self.add_state(enable)
        self.add_state(config)

        self.add_path(enable_to_shell)
        self.add_path(shell_to_enable)

        self.add_path(enable_to_config)
        self.add_path(config_to_enable)
