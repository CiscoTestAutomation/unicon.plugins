from unicon.plugins.generic import GenericSingleRpConnection
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider

from .. import NxosServiceList

from . import service_implementation as aci_svc
from .statemachine import AciStateMachine
from .settings import AciSettings


class AciN9KConnectionProvider(GenericSingleRpConnectionProvider):
    """
        Connection provider class for aci connections.
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the generic connection provider
        """
        super().__init__(*args, **kwargs)


class AciN9KServiceList(NxosServiceList):
    """ aci services. """

    def __init__(self):
        super().__init__()
        self.execute = aci_svc.Execute
        self.reload = aci_svc.Reload
        self.configure = aci_svc.Configure
        self.attach_console = aci_svc.AttachModuleConsole


class AciN9KConnection(GenericSingleRpConnection):
    """
        Connection class for aci connections.
    """

    os = 'nxos'
    platform = 'aci'
    chassis_type = 'single_rp'
    state_machine_class = AciStateMachine
    connection_provider_class = AciN9KConnectionProvider
    subcommand_list = AciN9KServiceList
    settings = AciSettings()
