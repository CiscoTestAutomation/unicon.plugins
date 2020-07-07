__author__ = "dwapstra"

from unicon.plugins.generic import GenericSingleRpConnection, service_implementation as svc
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider

from unicon.plugins.generic import ServiceList, service_implementation as svc
from . import service_implementation as staros_svc
from .statemachine import StarosStateMachine
from .settings import StarosSettings


class StarosConnectionProvider(GenericSingleRpConnectionProvider):
    """
        Connection provider class for staros connections.
    """
    pass


class StarosServiceList(ServiceList):
    """ staros services. """

    def __init__(self):
        self.send = svc.Send
        self.sendline = svc.Sendline
        self.expect = svc.Expect
        self.log_user = svc.LogUser
        self.command = staros_svc.Command
        self.execute = svc.Execute
        self.configure = staros_svc.Configure
        self.monitor = staros_svc.Monitor


class StarosConnection(GenericSingleRpConnection):
    """
        Connection class for staros connections.
    """
    os = 'staros'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = StarosStateMachine
    connection_provider_class = StarosConnectionProvider
    subcommand_list = StarosServiceList
    settings = StarosSettings()
