""" Generic IOS-XE State Machine """

__author__ = "Myles Dear <pyats-support@cisco.com>"

import re
from datetime import datetime
from unicon.plugins.generic.statemachine import (GenericSingleRpStateMachine, config_transition,
                                                 config_service_prompt_handler)
from unicon.plugins.generic.statements import (connection_statement_list,
                                               default_statement_list, wait_and_enter)
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

def enable_bash_console_transition(statemachine, spawn, context):
    ''' Transition from enable mode to bash_console

    Optional arguments are set by bash_console() (switch and rp).
    '''
    switch = context.get('_switch')
    rp = context.get('_rp')
    chassis = context.get('_chassis')
    cmd = 'request platform software system shell'
    if switch:
        cmd += f' switch {switch}'
    if rp:
        cmd += f' rp {rp}'
    if chassis:
        cmd += f' chassis {chassis}'
    spawn.sendline(cmd)


def boot_from_rommon(statemachine, spawn, context):
    context['boot_start_time'] = datetime.now()
    context['boot_prompt_count'] = 1
    boot_image(spawn, context, None)


def send_break(statemachine, spawn, context):
    spawn.send('\x03')


def enable_to_maintenance_transition(statemachine, spawn, context):

    dialog = Dialog([
        [patterns.want_continue_confirm, 'sendline()', None, True, False],
        [patterns.enable_prompt, wait_and_enter,
            {'wait': spawn.settings.MAINTENANCE_MODE_WAIT_TIME}, True, False],
        [patterns.maintenance_mode_prompt, None, None, False, False],
        [patterns.unable_to_create, 'sendline()', None, True, False]
    ])

    spawn.sendline(spawn.settings.MAINTENANCE_START_COMMAND)
    dialog.process(spawn, timeout=spawn.settings.MAINTENANCE_MODE_TIMEOUT)

    spawn.sendline()

def enable_to_acm_transition(state_machine, spawn, context):
    configlet_name = context.get('acm_configlet', '')
    spawn.sendline(f'acm configlet create {configlet_name}')

def enable_to_syntax_transition(state_machine, spawn, context):
    configlet_name = context.get('syntax_configlet', '')
    spawn.sendline(f'syntax configlet create {configlet_name}')

def maintenance_to_enable_transition(statemachine, spawn, context):

    dialog = Dialog([
        [patterns.want_continue_yes, 'sendline(yes)', None, True, False],
        [patterns.maintenance_mode_prompt,  wait_and_enter,
            {'wait': spawn.settings.MAINTENANCE_MODE_WAIT_TIME}, True, False],
        [patterns.enable_prompt, None, None, False, False],
        [patterns.unable_to_create, 'sendline()', None, True, False]
    ])

    spawn.sendline(spawn.settings.MAINTENANCE_STOP_COMMAND)
    dialog.process(spawn, timeout=spawn.settings.MAINTENANCE_MODE_TIMEOUT)

    spawn.sendline()


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
        acm = State('acm', patterns.acm_prompt)
        syntax = State('syntax', patterns.syntax_prompt)
        rules = State('rules', patterns.rules_prompt)
        macro = State('macro', patterns.macro_prompt)
        maintenance = State('maintenance', patterns.maintenance_mode_prompt)
        config_pki_hexmode = State('config_pki_hexmode', patterns.config_pki_prompt)

        disable_to_enable = Path(disable, enable, 'enable', Dialog([
            statements.password_stmt,
            statements.enable_password_stmt,
            statements.no_password_set_stmt,
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

        enable_to_acm = Path(enable, acm, enable_to_acm_transition, None)
        acm_to_enable = Path(acm, enable, 'end', None)

        enable_to_syntax = Path(enable, syntax, 'config check syntax', None)
        syntax_to_enable = Path(syntax, enable, 'end', None)
        enable_to_rules = Path(enable, rules, 'acm rules', None)
        rules_to_enable = Path(rules, enable, 'end', None)

        macro_to_config = Path(macro, config, send_break, None)

        enable_to_maintanance = Path(enable, maintenance, enable_to_maintenance_transition, None)
        maintenance_to_enable = Path(maintenance, enable, maintenance_to_enable_transition, None)

        config_pki_hexmode_to_config = Path(config_pki_hexmode, config, 'quit', None)

        self.add_state(disable)
        self.add_state(enable)
        self.add_state(config)
        self.add_state(guestshell)
        self.add_state(tclsh)
        self.add_state(acm)
        self.add_state(syntax)
        self.add_state(rules)
        self.add_state(macro)
        self.add_state(maintenance)
        self.add_state(config_pki_hexmode)

        self.add_path(disable_to_enable)
        self.add_path(enable_to_disable)
        self.add_path(enable_to_config)
        self.add_path(config_to_enable)
        self.add_path(enable_to_guestshell)
        self.add_path(guestshell_to_enable)
        self.add_path(enable_to_tclsh)
        self.add_path(tclsh_to_enable)
        self.add_path(enable_to_acm)
        self.add_path(acm_to_enable)
        self.add_path(enable_to_syntax)
        self.add_path(syntax_to_enable)
        self.add_path(enable_to_rules)
        self.add_path(rules_to_enable)
        self.add_path(macro_to_config)
        self.add_path(enable_to_maintanance)
        self.add_path(maintenance_to_enable)
        self.add_path(config_pki_hexmode_to_config)

        enable_to_rommon = Path(enable, rommon, 'reload', Dialog(
            connection_statement_list + reload_statement_list))

        rommon_to_disable = Path(rommon, disable, boot_from_rommon, Dialog(
            boot_from_rommon_statement_list))

        self.add_state(rommon)
        self.add_path(enable_to_rommon)
        self.add_path(rommon_to_disable)

        # Adding SHELL state to IOSXE platform.
        shell_dialog = Dialog([[patterns.access_shell, 'sendline(y)', None, True, False]])

        enable_to_shell = Path(enable, shell, enable_bash_console_transition, shell_dialog)
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
        acm = State('acm', patterns.acm_prompt)
        syntax = State('syntax', patterns.syntax_prompt)
        rules = State('rules', patterns.rules_prompt)
        macro = State('macro', patterns.macro_prompt)

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

        enable_to_acm = Path(enable, acm, enable_to_acm_transition, None)
        acm_to_enable = Path(acm, enable, 'end', None)

        enable_to_syntax = Path(enable, syntax, enable_to_syntax_transition, None)
        syntax_to_enable = Path(syntax, enable, 'end', None)
        enable_to_rules = Path(enable, rules, 'acm rules', None)
        rules_to_enable = Path(rules, enable, 'end', None)

        macro_to_config = Path(macro, config, send_break, None)

        self.add_state(disable)
        self.add_state(enable)
        self.add_state(config)
        self.add_state(rommon)
        self.add_state(tclsh)
        self.add_state(acm)
        self.add_state(syntax)
        self.add_state(rules)
        self.add_state(macro)

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
        self.add_path(enable_to_acm)
        self.add_path(acm_to_enable)
        self.add_path(enable_to_syntax)
        self.add_path(syntax_to_enable)
        self.add_path(enable_to_rules)
        self.add_path(rules_to_enable)
        self.add_path(macro_to_config)

        # Adding SHELL state to IOSXE platform.
        shell_dialog = Dialog([[patterns.access_shell, 'sendline(y)', None, True, False]])

        enable_to_shell = Path(enable, shell, enable_bash_console_transition, shell_dialog)
        shell_to_enable = Path(shell, enable, 'exit', None)

        # Add State and Path to State Machine
        self.add_state(shell)
        self.add_path(enable_to_shell)
        self.add_path(shell_to_enable)

        self.add_default_statements(default_statement_list)
