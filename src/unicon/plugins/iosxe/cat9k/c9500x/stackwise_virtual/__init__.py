""" A Stackwise-virtual C9500X IOS-XE connection implementation.
"""

from unicon.plugins.iosxe.stack import StackIosXEServiceList
from unicon.plugins.iosxe.stack import IosXEStackRPConnection
from unicon.plugins.iosxe.cat9k.stackwise_virtual.connection_provider import StackwiseVirtualConnectionProvider

from . import service_implementation as svc


class IosXEC9500xStackwiseVirtualServiceList(StackIosXEServiceList):

    def __init__(self):
        super().__init__()
        self.reload = svc.SVLStackReload
        self.switchover = svc.SVLStackSwitchover


class IosXEC9500xStackwiseVirtualRPConnection(IosXEStackRPConnection):
    os = 'iosxe'
    platform = 'cat9k'
    model = 'c9500'
    submodel = 'c9500x'
    chassis_type = 'stackwise_virtual'
    connection_provider_class = StackwiseVirtualConnectionProvider
    subcommand_list = IosXEC9500xStackwiseVirtualServiceList
