
from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider
from unicon.eal.dialogs import Dialog
from unicon.plugins.aireos.settings import AireosSettings
from unicon.plugins.aireos.statemachine import AireosStateMachine
from unicon.plugins.generic import ServiceList
from unicon.plugins.aireos import service_implementation as svc

from .patterns import AireosPatterns

p = AireosPatterns()


class AireosServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.reload = svc.AireosReload
        self.ping = svc.AireosPing
        self.copy = svc.AireosCopy
        self.execute = svc.AireosExecute
        self.configure = svc.AireosConfigure


class AireosConnection(BaseSingleRpConnection):
    os = 'aireos'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = AireosStateMachine
    connection_provider_class = GenericSingleRpConnectionProvider
    subcommand_list = AireosServiceList
    settings = AireosSettings()
