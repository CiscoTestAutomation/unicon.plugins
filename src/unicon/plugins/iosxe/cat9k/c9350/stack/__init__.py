""" A Stackwise-virtual c9350 IOS-XE connection implementation.
"""

from unicon.plugins.iosxe.stack import StackIosXEServiceList
from unicon.plugins.iosxe.stack import IosXEStackRPConnection, StackRpConnectionProvider
from . import service_implementation as svc

class IosXEC9350StackServiceList(StackIosXEServiceList):

    def __init__(self):
        super().__init__()
        self.reload = svc.C9350StackReload

class IosXEC9350StackRPConnection(IosXEStackRPConnection):
    os = 'iosxe'
    platform = 'cat9k'
    model = 'c9350'
    chassis_type = 'stack'
    connection_provider_class = StackRpConnectionProvider
    subcommand_list = IosXEC9350StackServiceList
