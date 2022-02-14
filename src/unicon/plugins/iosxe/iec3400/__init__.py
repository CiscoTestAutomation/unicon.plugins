
from unicon.plugins.iosxe import IosXEServiceList, IosXESingleRpConnection

from .settings import IosXEIec3400Settings
from . import service_implementation as svc
from .statemachine import IosXEIec3400SingleRpStateMachine


class IosXEIec3400ServiceList(IosXEServiceList):
    def __init__(self):
        super().__init__()
        self.reload = svc.Reload


class IosXEIec3400SingleRpConnection(IosXESingleRpConnection):
    os = 'iosxe'
    platform = 'iec3400'
    chassis_type = 'single_rp'
    state_machine_class = IosXEIec3400SingleRpStateMachine
    subcommand_list = IosXEIec3400ServiceList
    settings = IosXEIec3400Settings()
