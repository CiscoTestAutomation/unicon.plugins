""" ConfD CLI implementation """

__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import time

from unicon.eal.dialogs import Dialog

from unicon.plugins.generic import GenericSingleRpConnection, service_implementation as svc
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider

from unicon.plugins.confd.settings import ConfdSettings
from unicon.plugins.confd.patterns import ConfdPatterns
from unicon.plugins.confd.statemachine import ConfdStateMachine
from unicon.plugins.confd import service_implementation as confd_svc

from .statements import confd_statement_list

p = ConfdPatterns()


def wait_and_send_yes(spawn):
    time.sleep(0.1)
    spawn.sendline('yes')


class ConfdConnectionProvider(GenericSingleRpConnectionProvider):
    """
        Connection provided class for ConfD connections.
    """
    def get_connection_dialog(self):
        connection_dialogs = super().get_connection_dialog()
        connection_dialogs += Dialog(confd_statement_list)

        return connection_dialogs

    def set_init_commands(self):
        con = self.connection

        self.init_exec_commands = []
        self.init_config_commands = []

        if con.init_exec_commands is not None:
            self.init_exec_commands = con.init_exec_commands
        else:
            if con.state_machine.current_cli_style == 'cisco':
                self.init_exec_commands = con.settings.CISCO_INIT_EXEC_COMMANDS
            elif con.state_machine.current_cli_style == 'juniper':
                self.init_exec_commands = con.settings.JUNIPER_INIT_EXEC_COMMANDS

        if con.init_config_commands is not None:
            self.init_config_commands = con.init_config_commands
        else:
            if con.state_machine.current_cli_style == 'cisco':
                self.init_config_commands = con.settings.CISCO_INIT_CONFIG_COMMANDS
            elif con.state_machine.current_cli_style == 'juniper':
                self.init_config_commands = con.settings.JUNIPER_INIT_CONFIG_COMMANDS

    def execute_init_commands(self):
        self.set_init_commands()
        con = self.connection

        if len(self.init_exec_commands):
            con.execute(self.init_exec_commands, error_pattern=[])

        if len(self.init_config_commands):
            con.configure(self.init_config_commands, error_pattern=[])

    def init_handle(self):

        """ Executes the init commands on the device
        """
        con = self.connection
        con._is_connected = True

        con.state_machine.detect_state(con.spawn)
        if con.state_machine.current_cli_style == 'cisco':
            con.state_machine.go_to('cisco_exec',
                                    self.connection.spawn,
                                    context=self.connection.context,
                                    timeout=self.connection.connection_timeout)
        elif con.state_machine.current_cli_style == 'juniper':
            con.state_machine.go_to('juniper_exec',
                                    self.connection.spawn,
                                    context=self.connection.context,
                                    timeout=self.connection.connection_timeout)

        self.execute_init_commands()


class ConfdServiceList:
    """ ConfD services. """

    def __init__(self):
        self.send = svc.Send
        self.sendline = svc.Sendline
        self.expect = svc.Expect
        self.log_user = svc.LogUser
        self.execute = confd_svc.Execute
        self.configure = confd_svc.Configure
        self.cli_style = confd_svc.CliStyle
        self.command = confd_svc.Command
        self.expect_log = svc.ExpectLogging


class ConfdConnection(GenericSingleRpConnection):
    """
        Connection class for ConfD connections.
    """
    os = 'confd'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = ConfdStateMachine
    connection_provider_class = ConfdConnectionProvider
    subcommand_list = ConfdServiceList
    settings = ConfdSettings()

