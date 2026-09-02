""" ASRK IOS-XE connection implementation.

Overrides the HA reload service to use parallel processing
for active and standby RP boot output via ThreadPoolExecutor.
"""

from unicon.plugins.iosxe import (
    IosXEDualRPConnection,
    HAIosXEServiceList)

from . import service_implementation as svc


class AsrkHAIosXEServiceList(HAIosXEServiceList):
    def __init__(self):
        super().__init__()
        self.reload = svc.HAReload


class AsrkIosXEDualRPConnection(IosXEDualRPConnection):
    platform = 'asr1k'
    subcommand_list = AsrkHAIosXEServiceList
