""" cat9k IOS-XE connection implementation.
"""

__author__ = "Rob Trotter <rlt@cisco.com>"

from unicon.plugins.iosxe import (
    IosXESingleRpConnection,
    IosXEDualRPConnection,
    IosXEServiceList,
    HAIosXEServiceList)

from .statemachine import IosXECat9kSingleRpStateMachine, IosXECat9kDualRpStateMachine
from .settings import IosXECat9kSettings
from . import service_implementation as svc


class IosXECat9kServiceList(IosXEServiceList):
    def __init__(self):
        super().__init__()
        self.reload = svc.Reload
        self.rommon = svc.Rommon



class IosxeCat9kHAServiceList(HAIosXEServiceList):
    def __init__(self):
        super().__init__()
        self.reload = svc.HAReloadService


class IosXECat9kSingleRpConnection(IosXESingleRpConnection):
    platform = 'cat9k'
    state_machine_class = IosXECat9kSingleRpStateMachine
    subcommand_list = IosXECat9kServiceList
    settings = IosXECat9kSettings()


class IosXECat9kDualRPConnection(IosXEDualRPConnection):
    platform = 'cat9k'
    subcommand_list = IosxeCat9kHAServiceList
    settings = IosXECat9kSettings()
    state_machine_class = IosXECat9kDualRpStateMachine
