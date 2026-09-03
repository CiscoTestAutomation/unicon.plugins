from unicon.plugins.iosxe import (
    IosXEDualRPConnection, IosXESingleRpConnection,
    IosXEServiceList, HAIosXEServiceList
)
from unicon.plugins.iosxe.cat9k.service_implementation import (
    Rommon as Cat9kRommon,
    HARommon as Cat9kHARommon
)

from .settings import IosXEIe3kSettings


class IosXEIe3kServiceList(IosXEServiceList):
    def __init__(self):
        super().__init__()
        self.rommon = Cat9kRommon


class IosXEIe3kHAServiceList(HAIosXEServiceList):
    def __init__(self):
        super().__init__()
        self.rommon = Cat9kHARommon


class IosXEIe3kSingleRpConnection(IosXESingleRpConnection):
    platform = 'ie3k'
    subcommand_list = IosXEIe3kServiceList
    settings = IosXEIe3kSettings()


class IosXEIe3kDualRPConnection(IosXEDualRPConnection):
    platform = 'ie3k'
    subcommand_list = IosXEIe3kHAServiceList
    settings = IosXEIe3kSettings()
