""" Generic IOS-XE State Machine """

__author__ = "Myles Dear <pyats-support@cisco.com>"

import re
from datetime import datetime
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine, config_transition
from unicon.plugins.generic.statements import (connection_statement_list,
                                               default_statement_list)
from unicon.plugins.generic.service_statements import reload_statement_list
from unicon.plugins.generic.statements import GenericStatements, buffer_settled
from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog, Statement
from .patterns import IosXEPatterns
from .statements import (
    boot_image, boot_timeout_stmt,
    boot_from_rommon_statement_list)

patterns = IosXEPatterns()
statements = GenericStatements()


def boot_from_rommon(statemachine, spawn, context):
    context['boot_start_time'] = datetime.now()
    context['boot_prompt_count'] = 1
    boot_image(spawn, context, None)


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


class IosXESingleRpStateMachine(GenericSingleRpStateMachine):
    config_command = 'config term'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_transition_statement_list = [
            Statement(pattern=patterns.config_start,
                      action=config_service_prompt_handler,
                      args={'config_pattern': self.get_state('config').pattern},
                      loop_continue=True,
                      trim_buffer=False)
        ]

    def create(self):
        super().create()

        self.remove_path('enable', 'rommon')
        self.remove_path('rommon', 'disable')
        self.remove_state('rommon')
        self.remove_path('enable', 'disable')
        self.remove_path('disable', 'enable')
        self.remove_path('enable', 'config')
        self.remove_path('config', 'enable')
        self.remove_state('config')
        self.remove_state('enable')
        self.remove_state('disable')
        # incase there is no previous shell state registered
        try:
            self.remove_state('shell')
            self.remove_path('shell', 'enable')
            self.remove_path('enable', 'shell')
        except Exception:
            pass

        disable = State('disable', patterns.disable_prompt)
        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)
        shell = State('shell', patterns.shell_prompt)
        guestshell = State('guestshell', patterns.guestshell_prompt)
        rommon = State('rommon', patterns.rommon_prompt)
        tclsh = State('tclsh', patterns.tclsh_prompt)

        disable_to_enable = Path(disable, enable, 'enable', Dialog([
            statements.enable_password_stmt,
            statements.bad_password_stmt,
            statements.syslog_stripper_stmt
        ]))
        enable_to_disable = Path(enable, disable, 'disable', None)

        enable_to_config = Path(enable, config, config_transition, Dialog([statements.syslog_msg_stmt]))
        config_to_enable = Path(config, enable, 'end', Dialog([statements.syslog_msg_stmt]))

        enable_to_guestshell = Path(enable, guestshell, 'guestshell run bash', None)
        guestshell_to_enable = Path(guestshell, enable, 'exit', None)

        enable_to_tclsh = Path(enable, tclsh, 'tclsh', None)
        tclsh_to_enable = Path(tclsh, enable, 'exit', None)

        self.add_state(disable)
        self.add_state(enable)
        self.add_state(config)
        self.add_state(guestshell)
        self.add_state(tclsh)

        self.add_path(disable_to_enable)
        self.add_path(enable_to_disable)
        self.add_path(enable_to_config)
        self.add_path(config_to_enable)
        self.add_path(enable_to_guestshell)
        self.add_path(guestshell_to_enable)
        self.add_path(enable_to_tclsh)
        self.add_path(tclsh_to_enable)

        enable_to_rommon = Path(enable, rommon, 'reload', Dialog(
            connection_statement_list + reload_statement_list))

        rommon_to_disable = Path(rommon, disable, boot_from_rommon, Dialog(
            boot_from_rommon_statement_list))

        self.add_state(rommon)
        self.add_path(enable_to_rommon)
        self.add_path(rommon_to_disable)

        # Adding SHELL state to IOSXE platform.
        shell_dialog = Dialog([[patterns.access_shell, 'sendline(y)', None, True, False]])

        enable_to_shell = Path(enable, shell, 'request platform software system shell', shell_dialog)
        shell_to_enable = Path(shell, enable, 'exit', None)

        # Add State and Path to State Machine
        self.add_state(shell)
        self.add_path(enable_to_shell)
        self.add_path(shell_to_enable)


class IosXEDualRpStateMachine(StateMachine):
    config_command = 'config term'

    def create(self):
        # States
        disable = State('disable', patterns.disable_prompt)
        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)
        standby_locked = State('standby_locked', patterns.standby_locked)
        rommon = State('rommon', patterns.rommon_prompt)
        shell = State('shell', patterns.shell_prompt)
        tclsh = State('tclsh', patterns.tclsh_prompt)

        def update_cur_state(sm, state):
            sm._current_state = state

        # Paths
        disable_to_enable = Path(disable, enable, 'enable', Dialog([
            statements.enable_password_stmt,
            statements.bad_password_stmt,
            statements.syslog_stripper_stmt,
            Statement(
                pattern=patterns.standby_locked,
                action=update_cur_state,
                args={
                    'sm': self,
                    'state': 'standby_locked'
                },
                loop_continue=False)
        ]))

        enable_to_disable = Path(enable, disable, 'disable', Dialog([statements.syslog_msg_stmt]))

        enable_to_config = Path(enable, config, config_transition, Dialog([statements.syslog_msg_stmt]))

        config_to_enable = Path(config, enable, 'end', Dialog([statements.syslog_msg_stmt]))

        enable_to_rommon = Path(enable, rommon, 'reload', Dialog(
            connection_statement_list + reload_statement_list))

        rommon_to_disable = \
            Path(rommon, disable, boot_from_rommon, Dialog(
                boot_from_rommon_statement_list))

        enable_to_tclsh = Path(enable, tclsh, 'tclsh', None)
        tclsh_to_enable = Path(tclsh, enable, 'exit', None)

        self.add_state(disable)
        self.add_state(enable)
        self.add_state(config)
        self.add_state(rommon)
        self.add_state(tclsh)

        # Ensure that a locked standby is properly detected.
        # This is done by ensuring this is the last state added
        # so its state pattern is considered first.
        self.add_state(standby_locked)

        self.add_path(disable_to_enable)
        self.add_path(enable_to_disable)
        self.add_path(enable_to_config)
        self.add_path(config_to_enable)
        self.add_path(enable_to_rommon)
        self.add_path(rommon_to_disable)
        self.add_path(enable_to_tclsh)
        self.add_path(tclsh_to_enable)

        # Adding SHELL state to IOSXE platform.
        shell_dialog = Dialog([[patterns.access_shell, 'sendline(y)', None, True, False]])

        enable_to_shell = Path(enable, shell, 'request platform software system shell', shell_dialog)
        shell_to_enable = Path(shell, enable, 'exit', None)

        # Add State and Path to State Machine
        self.add_state(shell)
        self.add_path(enable_to_shell)
        self.add_path(shell_to_enable)

        self.add_default_statements(default_statement_list)
