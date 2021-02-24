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

from time import sleep

from unicon.core.errors import StateMachineError, TimeoutError as UniconTimeoutError
from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.generic.patterns import GenericPatterns

from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog, Statement

from .statements import (authentication_statement_list,
                         default_statement_list,
                         update_context)

patterns = GenericPatterns()
statements = GenericStatements()


def config_transition(statemachine, spawn, context):
    # Config may be locked, retry until max attempts or config state reached
    wait_time = spawn.settings.CONFIG_LOCK_RETRY_SLEEP
    max_attempts = spawn.settings.CONFIG_LOCK_RETRIES
    dialog = Dialog([Statement(pattern=patterns.config_locked,
                               action=update_context,
                               args={'config_locked': True},
                               loop_continue=False,
                               trim_buffer=True),
                     Statement(pattern=statemachine.get_state('enable').pattern,
                               action=update_context,
                               args={'config_locked': False},
                               loop_continue=False,
                               trim_buffer=False),
                     Statement(pattern=statemachine.get_state('config').pattern,
                               action=update_context,
                               args={'config_locked': False},
                               loop_continue=False,
                               trim_buffer=False)
                     ])

    for attempts in range(max_attempts + 1):
        spawn.sendline(statemachine.config_command)
        try:
            dialog.process(spawn, timeout=spawn.settings.CONFIG_TIMEOUT, context=context)
        except UniconTimeoutError:
            pass
        if context.get('config_locked'):
            if attempts < max_attempts:
                spawn.log.warning('*** Config lock detected, waiting {} seconds. Retry attempt {}/{} ***'.format(
                    wait_time, attempts + 1, max_attempts))
                sleep(wait_time)
        else:
            statemachine.detect_state(spawn)
            if statemachine.current_state == 'config':
                return
            else:
                spawn.log.warning("Could not enter config mode, sending clear line command and trying again..")
                spawn.send(spawn.settings.CLEAR_LINE_CMD)

    if context.get('config_locked'):
        raise StateMachineError('Config locked, unable to configure device')
    else:
        raise StateMachineError('Unable to transition to config mode')


#############################################################
# State Machine Definition
#############################################################

class GenericSingleRpStateMachine(StateMachine):
    config_command = 'config term'

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

        enable_to_disable = Path(enable, disable, 'disable', Dialog([statements.syslog_msg_stmt]))
        enable_to_rommon = Path(enable, rommon, 'reload', None)
        enable_to_config = Path(enable, config, config_transition, Dialog([statements.syslog_msg_stmt]))
        disable_to_enable = Path(disable, enable, 'enable',
                                 Dialog([statements.enable_password_stmt,
                                         statements.bad_password_stmt,
                                         statements.syslog_stripper_stmt]))
        config_to_enable = Path(config, enable, 'end', Dialog([statements.syslog_msg_stmt]))
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
