"""
Module:
    unicon.plugins.generic

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:

    This module implements a generic state machine which can be used
    by majority of the platforms. It should also be used as starting
    point by further sub classing it.
"""
from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.generic.patterns import GenericPatterns

from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog

from .statements import (authentication_statement_list,
                         default_statement_list)

patterns = GenericPatterns()
statements = GenericStatements()


#############################################################
# State Machine Definition
#############################################################

class GenericSingleRpStateMachine(StateMachine):

    """
        Defines Generic StateMachine for singleRP
        Statemachine keeps in track all the supported states
        for this platform, also have detail about moving from
        one state to another
    """

    def create(self):
        """creates the generic state machine"""

        ##########################################################
        # State Definition
        ##########################################################

        enable = State('enable', patterns.enable_prompt)
        disable = State('disable', patterns.disable_prompt)
        config = State('config', patterns.config_prompt)
        rommon = State('rommon', patterns.rommon_prompt)

        ##########################################################
        # Path Definition
        ##########################################################

        enable_to_disable = Path(enable, disable, 'disable', None)
        enable_to_config = Path(enable, config, 'config term', None)
        enable_to_rommon = Path(enable, rommon, 'reload', None)
        disable_to_enable = Path(disable, enable, 'enable',
                                 Dialog([statements.enable_password_stmt,
                                         statements.bad_password_stmt]))
        config_to_enable = Path(config, enable, 'end', None)
        rommon_to_disable = Path(rommon, disable, 'boot',
                                 Dialog(authentication_statement_list))

        self.add_state(enable)
        self.add_state(config)
        self.add_state(disable)
        self.add_state(rommon)

        self.add_path(rommon_to_disable)
        self.add_path(disable_to_enable)
        self.add_path(enable_to_config)
        self.add_path(enable_to_rommon)
        self.add_path(config_to_enable)
        self.add_path(enable_to_disable)
        self.add_default_statements(default_statement_list)

    def learn_os_state(self):
        learn_os = State('learn_os', patterns.learn_os_prompt)
        self.add_state(learn_os)


class GenericDualRpStateMachine(GenericSingleRpStateMachine):
    """
        Defines Generic StateMachine for dualRP
        Statemachine keeps in track all the supported states
        for this platform, also have detail about moving from
        one state to another.
    """

    def create(self):
        """creates the state machine"""

        super().create()

        ##########################################################
        # State Definition
        ##########################################################
        standby_locked = State('standby_locked', patterns.standby_locked)

        self.add_state(standby_locked)
