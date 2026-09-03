__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon.plugins.nxos.connection_provider import NxosSingleRpConnectionProvider
from unicon.plugins.nxos.connection_provider import NxosDualRpConnectionProvider
from unicon.plugins.nxos import NxosServiceList
from unicon.plugins.nxos import HANxosServiceList
from unicon.plugins.nxos import NxosSingleRpConnection
from unicon.plugins.nxos import NxosDualRPConnection
from unicon.plugins.nxos.setting import NxosSettings

from .statemachine import NxosMdsSingleRpStateMachine
from .statemachine import NxosMdsDualRpStateMachine

from . import service_implementation as svc


class NxosMdsServiceList(NxosServiceList):
    def __init__(self):
        super().__init__()
        self.tie = svc.Tie


class NxosMdsHaserviceList(HANxosServiceList):
    def __init__(self):
        super().__init__()
        self.tie = svc.Tie


class NxosMdsSingleRpConnection(NxosSingleRpConnection):
    os = 'nxos'
    platform = 'mds'
    chassis_type = 'single_rp'
    state_machine_class = NxosMdsSingleRpStateMachine
    connection_provider_class = NxosSingleRpConnectionProvider
    subcommand_list = NxosMdsServiceList
    settings = NxosSettings()


class NxosMdsDualRPConnection(NxosDualRPConnection):
    os = 'nxos'
    platform = 'mds'
    chassis_type = 'dual_rp'
    state_machine_class = NxosMdsDualRpStateMachine
    connection_provider_class = NxosDualRpConnectionProvider
    subcommand_list = NxosMdsHaserviceList
    settings = NxosSettings()

