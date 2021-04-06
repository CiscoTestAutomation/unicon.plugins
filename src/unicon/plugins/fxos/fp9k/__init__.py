__author__ = "dwapstra"

from .. import FxosConnectionProvider
from .. import FxosConnection
from .. import FxosSettings
from .. import FxosServiceList

from ..fp4k.statemachine import FxosFp4kStateMachine


class FxosFp9kConnection(FxosConnection):
    """
        Connection class for fxos/fp9k connections.
    """
    os = 'fxos'
    platform = 'fp9k'
    chassis_type = 'single_rp'
    state_machine_class = FxosFp4kStateMachine
    connection_provider_class = FxosConnectionProvider
    subcommand_list = FxosServiceList
    settings = FxosSettings()
