from unicon.eal.dialogs import Dialog
from unicon.plugins.generic import ServiceList, GenericSingleRpConnection, GenericDualRPConnection
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider

from unicon.plugins.generic import service_implementation as svc

from .patterns import AireosPatterns
from .settings import AireosSettings
from .statemachine import AireosStateMachine, AireosDualRpStateMachine
from .connection_provider import AireosDualRpConnectionProvider
from . import service_implementation as aireos_svc


p = AireosPatterns()


class AireosServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.reload = aireos_svc.AireosReload
        self.ping = aireos_svc.AireosPing
        self.copy = aireos_svc.AireosCopy
        self.execute = aireos_svc.AireosExecute
        self.configure = aireos_svc.AireosConfigure


class HAAireosServiceList(AireosServiceList):
    def __init__(self):
        super().__init__()
        self.execute = aireos_svc.AireosHaExecute


class AireosConnection(GenericSingleRpConnection):
    os = 'aireos'
    platform = None
    chassis_type = 'single_rp'
    state_machine_class = AireosStateMachine
    connection_provider_class = GenericSingleRpConnectionProvider
    subcommand_list = AireosServiceList
    settings = AireosSettings()


class AireosDualRPConnection(GenericDualRPConnection):
    os = 'aireos'
    platform = None
    chassis_type = 'dual_rp'
    subcommand_list = HAAireosServiceList
    state_machine_class = AireosDualRpStateMachine
    connection_provider_class = AireosDualRpConnectionProvider
    settings = AireosSettings()
