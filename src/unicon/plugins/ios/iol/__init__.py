__author__ = 'Difu Hu <difhu@cisco.com>'

from unicon.plugins.generic import GenericDualRPConnection, HAServiceList

from .service_implementation import IosIolSwitchoverService


class IosIolHAServiceList(HAServiceList):
    def __init__(self):
        super().__init__()
        self.switchover = IosIolSwitchoverService


class IosIolDualRPConnection(GenericDualRPConnection):
    os = 'ios'
    platform = 'iol'
    subcommand_list = IosIolHAServiceList
