from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider
from unicon.plugins.generic import GenericSingleRpConnection, ServiceList
from unicon.plugins.fxos import service_implementation as fxos_svc

from . import service_implementation as svc

from .statemachine import AsaFp2kStateMachine
from .settings import AsaFp2kSettings


class AsaFp2kConnectionProvider(GenericSingleRpConnectionProvider):
    """
        Connection provider class for fp2k connections.
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the generic connection provider
        """
        super().__init__(*args, **kwargs)
        self.connection.settings.MORE_CONTINUE = 'q'

    def init_handle(self):
        con = self.connection
        con.state_machine.detect_state(con.spawn)
        self.execute_init_commands()
        self.connection.settings.MORE_CONTINUE = ' '


class AsaFp2kServiceList(ServiceList):
    """ fp2k services. """

    def __init__(self):
        super().__init__()
        self.fxos = fxos_svc.FXOS
        self.fxos_mgmt = fxos_svc.FXOSManagement
        self.sudo = fxos_svc.Sudo
        self.disable = fxos_svc.Disable
        self.enable = fxos_svc.Enable
        self.reload = svc.Reload
        self.switchto = svc.Switchto
        self.rommon = fxos_svc.Rommon


class AsaFp2kConnection(GenericSingleRpConnection):
    """
        Connection class for fp2k connections.
    """
    os = 'asa'
    platform = 'fp2k'
    chassis_type = 'single_rp'
    state_machine_class = AsaFp2kStateMachine
    connection_provider_class = AsaFp2kConnectionProvider
    subcommand_list = AsaFp2kServiceList
    settings = AsaFp2kSettings()
