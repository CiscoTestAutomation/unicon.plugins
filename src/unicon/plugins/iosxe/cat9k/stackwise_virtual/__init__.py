""" A Stackwise-virtual IOS-XE connection implementation.
"""

from unicon.plugins.iosxe.stack import StackIosXEServiceList
from unicon.plugins.iosxe.stack import IosXEStackRPConnection
from .connection_provider import StackwiseVirtualConnectionProvider

from unicon.plugins.iosxe.stack.service_implementation import StackReload, StackSwitchover


class IosXECat9kStackwiseVirtualServiceList(StackIosXEServiceList):

    def __init__(self):
        super().__init__()
        self.reload = StackReload
        self.switchover = StackSwitchover


class IosXECat9kStackwiseVirtualRPConnection(IosXEStackRPConnection):
    os = 'iosxe'
    platform = 'cat9k'
    chassis_type = 'stackwise_virtual'
    connection_provider_class = StackwiseVirtualConnectionProvider
    subcommand_list = IosXECat9kStackwiseVirtualServiceList
