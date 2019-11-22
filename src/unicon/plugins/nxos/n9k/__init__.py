__author__ = 'Difu Hu <difhu@cisco.com>'

from unicon.plugins.nxos import NxosServiceList, HANxosServiceList
from unicon.plugins.nxos import NxosSingleRpConnection, NxosDualRPConnection

from .setting import Nxos9kSettings
from .service_implementation import Nxos9kReload, HANxos9kReloadService


class Nxos9kServiceList(NxosServiceList):
    def __init__(self):
        super().__init__()
        self.reload = Nxos9kReload


class HANxos9kServiceList(HANxosServiceList):
    def __init__(self):
        super().__init__()
        self.reload = HANxos9kReloadService


class Nxos9kSingleRpConnection(NxosSingleRpConnection):
    series = 'n9k'
    subcommand_list = Nxos9kServiceList
    settings = Nxos9kSettings()


class Nxos9kDualRPConnection(NxosDualRPConnection):
    series = 'n9k'
    subcommand_list = HANxos9kServiceList
    settings = Nxos9kSettings()
