""" CAT4K IOS-XE connection implementation.
"""

from unicon.plugins.iosxe import IosXESingleRpConnection, IosXEDualRPConnection

from .. import IosXEServiceList

from .settings import IosXECat4kSettings
from . import service_implementation as svc
from .connection_provider import Cat4kDualRpConnectionProvider


class IosXECat4kServiceList(IosXEServiceList):
    def __init__(self):
        super().__init__()
        self.execute= svc.Execute
        self.config=svc.Configure
        self.reload=svc.Reload

class IosXECat4kSingleRpConnection(IosXESingleRpConnection):
    platform = 'cat4k'
    settings=IosXECat4kSettings()

class IosXECat4kDualRPConnection(IosXEDualRPConnection):
    platform = 'cat4k'
    chassis_type= 'dual_rp'
    connection_provider_class=Cat4kDualRpConnectionProvider
    subcommand_list = IosXECat4kServiceList
    settings=IosXECat4kSettings()