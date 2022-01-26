
from unicon.plugins.iosxe.c9800 import IosXEc9800ServiceList, IosXEc9800SingleRpConnection, IosXEc9800DualRPConnection


class IosXEc9800CLServiceList(IosXEc9800ServiceList):
    def __init__(self):
        super().__init__()



class IosXEc9800CLSingleRpConnection(IosXEc9800SingleRpConnection):
    os = 'iosxe'
    platform = 'c9800'
    model = 'c9800_cl'
    subcommand_list = IosXEc9800CLServiceList


class IosXEc9800CLDualRpConnection(IosXEc9800DualRPConnection):
    os = 'iosxe'
    platform = 'c9800'
    model = 'c9800_cl'
    subcommand_list = IosXEc9800CLServiceList
