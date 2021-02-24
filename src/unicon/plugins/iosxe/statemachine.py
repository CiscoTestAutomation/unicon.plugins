""" Generic IOS-XE State Machine """

__author__ = "Myles Dear <pyats-support@cisco.com>"

from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine, config_transition
from unicon.plugins.generic.statements import (connection_statement_list,
                                               default_statement_list)
from unicon.plugins.generic.service_statements import reload_statement_list
from unicon.plugins.generic.statements import GenericStatements
from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog
from .patterns import IosXEPatterns
from .statements import boot_from_rommon_statement_list

patterns = IosXEPatterns()
statements = GenericStatements()


class IosXESingleRpStateMachine(GenericSingleRpStateMachine):
    config_command = 'config term'

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
        # incase there is no previous shell state regiestered
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

        disable_to_enable = Path(disable, enable, 'enable', Dialog([
            statements.enable_password_stmt,
            statements.bad_password_stmt,
            statements.syslog_stripper_stmt
        ]))
        enable_to_disable = Path(enable, disable, 'disable', None)

        enable_to_config = Path(enable, config, config_transition, Dialog([statements.syslog_msg_stmt]))
        config_to_enable = Path(config, enable, 'end', Dialog([statements.syslog_msg_stmt]))

        self.add_state(disable)
        self.add_state(enable)
        self.add_state(config)

        self.add_path(disable_to_enable)
        self.add_path(enable_to_disable)
        self.add_path(enable_to_config)
        self.add_path(config_to_enable)

        rommon = State('rommon', patterns.rommon_prompt)
        enable_to_rommon = Path(enable, rommon, 'reload',
            Dialog(connection_statement_list + reload_statement_list))
        rommon_to_disable = \
            Path(rommon, disable, '\r', Dialog(
                connection_statement_list + boot_from_rommon_statement_list))
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

        # Paths
        disable_to_enable = Path(disable, enable, 'enable', Dialog([
            statements.enable_password_stmt,
            statements.bad_password_stmt,
            statements.syslog_stripper_stmt
        ]))

        enable_to_disable = Path(enable, disable, 'disable', Dialog([statements.syslog_msg_stmt]))

        enable_to_config = Path(enable, config, config_transition, Dialog([statements.syslog_msg_stmt]))

        config_to_enable = Path(config, enable, 'end', Dialog([statements.syslog_msg_stmt]))

        enable_to_rommon = Path(enable, rommon, 'reload', Dialog(
            connection_statement_list + reload_statement_list))

        rommon_to_disable = \
            Path(rommon, disable, '\r', Dialog(
                connection_statement_list + boot_from_rommon_statement_list))

        self.add_state(disable)
        self.add_state(enable)
        self.add_state(config)
        self.add_state(rommon)

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

        # Adding SHELL state to IOSXE platform.
        shell_dialog = Dialog([[patterns.access_shell, 'sendline(y)', None, True, False]])

        enable_to_shell = Path(enable, shell, 'request platform software system shell', shell_dialog)
        shell_to_enable = Path(shell, enable, 'exit', None)

        # Add State and Path to State Machine
        self.add_state(shell)
        self.add_path(enable_to_shell)
        self.add_path(shell_to_enable)

        self.add_default_statements(default_statement_list)
