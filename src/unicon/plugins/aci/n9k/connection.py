import warnings
from unicon.plugins.generic import GenericSingleRpConnection, service_implementation as svc
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider

from unicon.plugins.generic import ServiceList, service_implementation as svc
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

        warnings.warn("This plugin aci/n9k wil be deprecated, it has been"
            "moved under nxos. Please set it in the testbed yaml file as "
            "follows:\nos: nxos\nseries: aci" , DeprecationWarning)

        super().__init__(*args, **kwargs)


class AciN9KServiceList(ServiceList):
    """ aci services. """

    def __init__(self):
        super().__init__()
        self.execute = aci_svc.Execute
        self.reload = aci_svc.Reload


class AciN9KConnection(GenericSingleRpConnection):
    """
        Connection class for aci connections.
    """

    os = 'aci'
    series = 'n9k'
    chassis_type = 'single_rp'
    state_machine_class = AciStateMachine
    connection_provider_class = AciN9KConnectionProvider
    subcommand_list = AciN9KServiceList
    settings = AciSettings()
