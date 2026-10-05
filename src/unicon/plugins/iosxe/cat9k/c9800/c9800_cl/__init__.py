
from unicon.plugins.iosxe.cat9k.c9800 import (
    IosXEc9800DualRPConnection,
    IosXEc9800ServiceList,
    IosXEc9800SingleRpConnection,
)
from unicon.plugins.iosxe import service_implementation as svc

from .statemachine import IosXEc9800CLSingleRpStateMachine


class IosXEc9800CLServiceList(IosXEc9800ServiceList):
    def __init__(self):
        super().__init__()
        self.rommon = svc.Rommon



class IosXEc9800CLSingleRpConnection(IosXEc9800SingleRpConnection):
    os = 'iosxe'
    platform = 'cat9k'
    model = 'c9800'
    submodel = 'c9800_cl'
    state_machine_class = IosXEc9800CLSingleRpStateMachine
    subcommand_list = IosXEc9800CLServiceList


class IosXEc9800CLDualRpConnection(IosXEc9800DualRPConnection):
    os = 'iosxe'
    platform = 'cat9k'
    model = 'c9800'
    submodel = 'c9800_cl'
    subcommand_list = IosXEc9800CLServiceList
