__author__ = 'Dave Wapstra <dwapstra@cisco.com>'

from unicon.plugins.nxos import (
    NxosServiceList, HANxosServiceList,
    NxosSingleRpConnection, NxosDualRPConnection)

from .setting import Nxos7kSettings
from .connection_provider import Nxos7kSingleRpConnectionProvider, Nxos7kDualRpConnectionProvider


class Nxos7kServiceList(NxosServiceList):
    def __init__(self):
        super().__init__()


class HANxos7kServiceList(HANxosServiceList):
    def __init__(self):
        super().__init__()


class Nxos7kSingleRpConnection(NxosSingleRpConnection):
    platform = 'n7k'
    subcommand_list = Nxos7kServiceList
    settings = Nxos7kSettings()
    connection_provider_class = Nxos7kSingleRpConnectionProvider


class Nxos7kDualRPConnection(NxosDualRPConnection):
    platform = 'n7k'
    subcommand_list = HANxos7kServiceList
    settings = Nxos7kSettings()
    connection_provider_class = Nxos7kDualRpConnectionProvider
