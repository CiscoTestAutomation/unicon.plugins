""" cat8k IOS-XE connection implementation.
"""

__author__ = "Lukas McClelland <lumcclel@cisco.com>"

from .. import IosXEServiceList
from .settings import IosXECat8kSettings
from . import service_implementation as svc
from .statemachine import IosXECat8kSingleRpStateMachine

from unicon.plugins.iosxe import IosXESingleRpConnection


class IosXECat8kServiceList(IosXEServiceList):
    def __init__(self):
        super().__init__()
        self.switchover = svc.SwitchoverService


class IosXECat8kSingleRpConnection(IosXESingleRpConnection):
    platform = 'cat8k'
    state_machine_class = IosXECat8kSingleRpStateMachine
    subcommand_list = IosXECat8kServiceList
    settings = IosXECat8kSettings()
