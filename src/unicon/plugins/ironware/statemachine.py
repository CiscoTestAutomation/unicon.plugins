"""
Module:
    unicon.plugins.ironware.state_machine

Author:
    James Di Trapani <james@ditrapani.com.au> - https://github.com/jamesditrapani

Description:
    Enables connection handle to transition into different router states,
    specific to the Ironware NOS.
"""

__author__ = "James Di Trapani <james@ditrapani.com.au>"

from unicon.statemachine import Path
from unicon.eal.dialogs import Dialog
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine
from .patterns import IronWarePatterns

patterns = IronWarePatterns()


class IronWareSingleRpStateMachine(GenericSingleRpStateMachine):

    def create(self):
        '''
        statemachine class's create() method is its entrypoint. This showcases
        how to setup a statemachine in Unicon.
        '''
        super().create()

        # remove some known path
        enable = self.get_state('enable')
        enable.pattern = patterns.privileged_mode

        disable = self.get_state('disable')
        disable.pattern = patterns.disable_mode

        config = self.get_state('config')
        config.pattern = patterns.config_mode