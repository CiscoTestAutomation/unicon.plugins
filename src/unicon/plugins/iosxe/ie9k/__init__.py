from unicon.plugins.iosxe import IosXEDualRPConnection, IosXESingleRpConnection

from .settings import IosXEIe9kSettings


class IosXEIe9kSingleRpConnection(IosXESingleRpConnection):
    platform = 'ie9k'
    settings = IosXEIe9kSettings()


class IosXEIe9kDualRPConnection(IosXEDualRPConnection):
    platform = 'ie9k'
    settings = IosXEIe9kSettings()
