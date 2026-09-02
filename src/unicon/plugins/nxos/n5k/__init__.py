__author__ = "Myles Dear <mdear@cisco.com>"

from .. import (NxosServiceList, NxosSingleRpConnection,
    NxosSingleRpConnectionProvider, NxosSettings, )

from ..statemachine import NxosSingleRpStateMachine

from unicon.plugins.nxos.n5k import service_implementation as svc

class NxosN5kServiceList(NxosServiceList):
    def __init__(self):
        super().__init__()
        self.reload = svc.Reload



class NxosN5kSingleRpConnection(NxosSingleRpConnection):
    os = 'nxos'
    platform = 'n5k'
    chassis_type = 'single_rp'
    state_machine_class = NxosSingleRpStateMachine
    connection_provider_class = NxosSingleRpConnectionProvider
    subcommand_list = NxosN5kServiceList
    settings = NxosSettings()
