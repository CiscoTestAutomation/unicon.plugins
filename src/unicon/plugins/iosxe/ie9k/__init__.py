from unicon.plugins.iosxe import IosXEDualRPConnection, IosXESingleRpConnection
from unicon.plugins.iosxe.ie3k import IosXEIe3kServiceList, IosXEIe3kHAServiceList

from .settings import IosXEIe9kSettings


class IosXEIe9kServiceList(IosXEIe3kServiceList):
    def __init__(self):
        super().__init__()


class IosxeIe9kHAServiceList(IosXEIe3kHAServiceList):
    def __init__(self):
        super().__init__()


class IosXEIe9kSingleRpConnection(IosXESingleRpConnection):
    platform = 'ie9k'
    subcommand_list = IosXEIe9kServiceList
    settings = IosXEIe9kSettings()


class IosXEIe9kDualRPConnection(IosXEDualRPConnection):
    platform = 'ie9k'
    subcommand_list = IosxeIe9kHAServiceList
    settings = IosXEIe9kSettings()
