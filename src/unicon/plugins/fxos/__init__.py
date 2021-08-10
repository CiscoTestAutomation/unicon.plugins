__author__ = "dwapstra"

from unicon.plugins.generic import GenericSingleRpConnection, ServiceList
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider

from . import service_implementation as svc
from .statemachine import FxosStateMachine
from .settings import FxosSettings


class FxosConnectionProvider(GenericSingleRpConnectionProvider):
    """
        Connection provider class for fxos connections.
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the generic connection provider
        """
        super().__init__(*args, **kwargs)
        self.connection.settings.MORE_CONTINUE = 'q'

    def init_handle(self):
        con = self.connection
        self.execute_init_commands()
        self.connection.settings.MORE_CONTINUE = ' '


class FxosServiceList(ServiceList):
    """ fxos services. """

    def __init__(self):
        super().__init__()
        self.switchto = svc.Switchto
        self.fireos = svc.FireOS
        self.ftd = svc.FTD
        self.fxos = svc.FXOS
        self.fxos_mgmt = svc.FXOSManagement
        self.expert = svc.Expert
        self.sudo = svc.Sudo
        self.disable = svc.Disable
        self.enable = svc.Enable
        self.rommon = svc.Rommon
        self.reload = svc.Reload


class FxosConnection(GenericSingleRpConnection):
    """
        Connection class for fxos connections.
    """
    os = 'fxos'
    platform = None
    chassis_type = 'single_rp'
    state_machine_class = FxosStateMachine
    connection_provider_class = FxosConnectionProvider
    subcommand_list = FxosServiceList
    settings = FxosSettings()
