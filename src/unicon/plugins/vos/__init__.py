__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon.plugins.generic import GenericSingleRpConnection, service_implementation as svc
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider

from unicon.plugins.generic import ServiceList, service_implementation as svc
from . import service_implementation as vos_svc
from .statemachine import VosStateMachine
from .settings import VosSettings


class VosConnectionProvider(GenericSingleRpConnectionProvider):
    """
        Connection provider class for vos connections.
    """

    def init_handle(self):
        con = self.connection
        con.connection_timeout = 300
        con.state_machine.go_to('shell',
                                self.connection.spawn,
                                context=self.connection.context,
                                prompt_recovery=self.prompt_recovery,
                                timeout=self.connection.connection_timeout)

        self.execute_init_commands()


class VosServiceList(ServiceList):
    """ vos services. """

    def __init__(self):
        self.send = svc.Send
        self.sendline = svc.Sendline
        self.expect = svc.Expect
        self.execute = vos_svc.Execute
        self.log_user = svc.LogUser


class VosConnection(GenericSingleRpConnection):
    """
        Connection class for vos connections.
    """
    os = 'vos'
    platform = None
    chassis_type = 'single_rp'
    state_machine_class = VosStateMachine
    connection_provider_class = VosConnectionProvider
    subcommand_list = VosServiceList
    settings = VosSettings()
