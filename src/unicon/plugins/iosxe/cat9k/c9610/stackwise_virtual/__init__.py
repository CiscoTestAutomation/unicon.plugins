""" A Stackwise-virtual C9610 IOS-XE connection implementation.
"""

from unicon.plugins.iosxe.stack import StackIosXEServiceList
from unicon.plugins.iosxe.stack import IosXEStackRPConnection
from unicon.plugins.iosxe.cat9k.stackwise_virtual.connection_provider import StackwiseVirtualConnectionProvider

from unicon.plugins.iosxe.cat9k.c9500x.stackwise_virtual.service_implementation import SVLStackReload, SVLStackSwitchover


class IosXEC9610StackwiseVirtualServiceList(StackIosXEServiceList):

    def __init__(self):
        super().__init__()
        self.reload = SVLStackReload
        self.switchover = SVLStackSwitchover


class IosXEC9610StackwiseVirtualRPConnection(IosXEStackRPConnection):
    os = 'iosxe'
    platform = 'cat9k'
    model = 'c9610'
    submodel = 'c9610'
    chassis_type = 'stackwise_virtual'
    connection_provider_class = StackwiseVirtualConnectionProvider
    subcommand_list = IosXEC9610StackwiseVirtualServiceList
