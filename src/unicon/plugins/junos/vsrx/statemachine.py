"""
Module:
    unicon.plugins.junos.vsrx

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:

    This module implements a Junos vSRX state machine.
"""
from unicon.plugins.junos.patterns import JunosPatterns
from unicon.statemachine import State, Path
from unicon.eal.dialogs import Statement, Dialog
from unicon.plugins.junos.statemachine import JunosSingleRpStateMachine

patterns = JunosPatterns()


class JunosVsrxSingleRpStateMachine(JunosSingleRpStateMachine):

    """
        Defines Junos StateMachine for singleRP
        Statemachine keeps in track all the supported states
        for this platform, also have detail about moving from
        one state to another
    """

    def create(self):
        """creates the junos state machine"""

        JunosSingleRpStateMachine.create(self)
        ##########################################################
        # Get parent State
        ##########################################################
        shell = self.get_state('shell')
        enable = self.get_state('enable')

        ##########################################################
        # Overwrite parent Path
        ##########################################################
        self.remove_path(shell, enable)
        self.remove_path(enable, shell)

        enable_to_shell = Path(enable, shell, 'start shell', None)
        shell_to_enable = Path(shell, enable, 'exit', None)

        self.add_path(enable_to_shell)
        self.add_path(shell_to_enable)

