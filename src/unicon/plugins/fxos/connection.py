from unicon.plugins.generic import GenericSingleRpConnection, service_implementation as svc
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider

from unicon.plugins.generic import ServiceList, service_implementation as svc
from .statemachine import FxosStateMachine
from .settings import FxosSettings

class FxosConnectionProvider(GenericSingleRpConnectionProvider):
    """
        Connection provider class for fxos connections.
    """

    def init_handle(self):
        con = self.connection
        con._is_connected = True
        self.execute_init_commands()


class FxosServiceList(ServiceList):
    """ fxos services. """

    def __init__(self):
        super().__init__()


class FxosConnection(GenericSingleRpConnection):
    """
        Connection class for fxos connections.
    """
    os = 'fxos'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = FxosStateMachine
    connection_provider_class = FxosConnectionProvider
    subcommand_list = FxosServiceList
    settings = FxosSettings()