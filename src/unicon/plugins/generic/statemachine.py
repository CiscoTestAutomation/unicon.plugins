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

import re
from time import sleep

from unicon.core.errors import StateMachineError
from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.generic.patterns import GenericPatterns

from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog, Statement

from .statements import (authentication_statement_list,
                         default_statement_list, buffer_settled)

patterns = GenericPatterns()
statements = GenericStatements()


def config_service_prompt_handler(spawn, config_pattern):
    """ Check if we need to send the sevice config prompt command.
    """
    if hasattr(spawn.settings, 'SERVICE_PROMPT_CONFIG_CMD') and spawn.settings.SERVICE_PROMPT_CONFIG_CMD:
        # if the config prompt is seen, return
        if re.search(config_pattern, spawn.buffer):
            return
        else:
            # if no buffer changes for a few seconds, check again
            if buffer_settled(spawn, spawn.settings.CONFIG_PROMPT_WAIT):
                if re.search(config_pattern, spawn.buffer):
                    return
                else:
                    spawn.sendline(spawn.settings.SERVICE_PROMPT_CONFIG_CMD)


def config_transition(statemachine, spawn, context):
    # Config may be locked, retry until max attempts or config state reached
    wait_time = spawn.settings.CONFIG_LOCK_RETRY_SLEEP
    max_attempts = spawn.settings.CONFIG_LOCK_RETRIES
    dialog = Dialog([Statement(pattern=statemachine.get_state('enable').pattern,
                               loop_continue=False,
                               trim_buffer=True),
                     Statement(pattern=statemachine.get_state('config').pattern,
                               loop_continue=False,
                               trim_buffer=False),
                     Statement(pattern=patterns.config_start,
                               action=config_service_prompt_handler,
                               args={'config_pattern': statemachine.get_state('config').pattern},
                               loop_continue=True,
                               trim_buffer=False)
                     ])

    for attempt in range(max_attempts + 1):
        spawn.sendline(statemachine.config_command)
        dialog.process(spawn, timeout=spawn.settings.CONFIG_TIMEOUT, context=context)

        statemachine.detect_state(spawn)
        if statemachine.current_state == 'config':
            return

        if attempt < max_attempts:
            spawn.log.warning('*** Could not enter config mode, waiting {} seconds. Retry attempt {}/{} ***'.format(
                              wait_time, attempt + 1, max_attempts))
            sleep(wait_time)

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
