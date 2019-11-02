__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon_plugins.plugins.nxos.connection_provider import NxosSingleRpConnectionProvider
from unicon_plugins.plugins.nxos.connection_provider import NxosDualRpConnectionProvider
from unicon_plugins.plugins.nxos import NxosServiceList
from unicon_plugins.plugins.nxos import HANxosServiceList
from unicon_plugins.plugins.nxos import NxosSingleRpConnection
from unicon_plugins.plugins.nxos import NxosDualRPConnection
from unicon_plugins.plugins.nxos.setting import NxosSettings

from .statemachine import NxosMdsSingleRpStateMachine
from .statemachine import NxosMdsDualRpStateMachine


class NxosMdsSingleRpConnection(NxosSingleRpConnection):
    os = 'nxos'
    series = 'mds'
    chassis_type = 'single_rp'
    state_machine_class = NxosMdsSingleRpStateMachine
    connection_provider_class = NxosSingleRpConnectionProvider
    subcommand_list = NxosServiceList
    settings = NxosSettings()


class NxosMdsDualRPConnection(NxosDualRPConnection):
    os = 'nxos'
    series = 'mds'
    chassis_type = 'dual_rp'
    state_machine_class = NxosMdsDualRpStateMachine
    connection_provider_class = NxosDualRpConnectionProvider
    subcommand_list = HANxosServiceList
    settings = NxosSettings()

