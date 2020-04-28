from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider

from unicon.plugins.generic import ServiceList
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


class AciN9KServiceList(ServiceList):
    """ aci services. """

    def __init__(self):
        super().__init__()
        self.execute = aci_svc.Execute
        self.reload = aci_svc.Reload