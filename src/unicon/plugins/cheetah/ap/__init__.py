__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"


from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine
from unicon.plugins.generic import ServiceList
from unicon.plugins.generic import GenericSingleRpConnectionProvider
from unicon.plugins.cheetah.ap.settings import ApSettings
from unicon.plugins.cheetah.ap import service_implementation as svc
from unicon.plugins.generic import service_implementation as gsvc


class ApServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.execute = svc.Execute
        self.send = gsvc.Send
        self.sendline = gsvc.Sendline
        self.expect = gsvc.Expect
        self.enable = gsvc.Enable
        self.disable = gsvc.Disable
        self.reload = gsvc.Reload
        self.log_user = gsvc.LogUser


class ApSingleRpConnectionProvider(GenericSingleRpConnectionProvider):

    def set_init_commands(self):
        con = self.connection

        if con.init_exec_commands is not None:
            self.init_exec_commands = con.init_exec_commands
        else:
            self.init_exec_commands = con.settings.HA_INIT_EXEC_COMMANDS

        if con.init_config_commands is not None:
            self.init_config_commands = con.init_config_commands
        else:
            self.init_config_commands = []

    def init_handle(self):
        con = self.connection
        con.state_machine.go_to('enable',
                                self.connection.spawn,
                                context=self.connection.context,
                                timeout=self.connection.connection_timeout)
        self.execute_init_commands()


class ApSingleRpConnection(BaseSingleRpConnection):
    os = 'cheetah'
    platform = 'ap'
    chassis_type = 'single_rp'
    state_machine_class = GenericSingleRpStateMachine
    connection_provider_class = ApSingleRpConnectionProvider
    subcommand_list = ApServiceList
    settings = ApSettings()
