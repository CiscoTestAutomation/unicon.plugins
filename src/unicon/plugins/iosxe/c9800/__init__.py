""" C9800 connection implementation.
"""

from unicon.plugins.iosxe import IosXESingleRpConnection, IosXEDualRPConnection

from .. import IosXEServiceList

from .statemachine import IosXEc9800SingleRpStateMachine
from .settings import IosXEc9800Settings
from ..cat9k import service_implementation as svc


class IosXEc9800ServiceList(IosXEServiceList):
    def __init__(self):
        super().__init__()
        self.reload = svc.Reload
        self.rommon = svc.Rommon


class IosXEc9800SingleRpConnection(IosXESingleRpConnection):
    platform = 'c9800'
    state_machine_class = IosXEc9800SingleRpStateMachine
    subcommand_list = IosXEc9800ServiceList
    settings = IosXEc9800Settings()


class IosXEc9800DualRPConnection(IosXEDualRPConnection):
    platform = 'c9800'
    settings = IosXEc9800Settings()
