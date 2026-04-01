from unicon.plugins.iosxe import IosXEDualRPConnection, IosXESingleRpConnection

from .settings import IosXEIe3kSettings


class IosXEIe3kSingleRpConnection(IosXESingleRpConnection):
    platform = 'ie3k'
    settings = IosXEIe3kSettings()


class IosXEIe3kDualRPConnection(IosXEDualRPConnection):
    platform = 'ie3k'
    settings = IosXEIe3kSettings()
