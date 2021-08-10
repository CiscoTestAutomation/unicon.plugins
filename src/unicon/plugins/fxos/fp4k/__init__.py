__author__ = "dwapstra"

from .. import FxosConnectionProvider
from .. import FxosConnection
from .. import FxosServiceList

from .settings import FxosFp4kSettings
from .statemachine import FxosFp4kStateMachine
from . import service_implementation as svc


class FxosF4pkServiceList(FxosServiceList):
    """ fxos services. """

    def __init__(self):
        super().__init__()
        self.reload = svc.Reload


class FxosFp4kConnection(FxosConnection):
    """
        Connection class for fxos/fp4k connections.
    """
    os = 'fxos'
    platform = 'fp4k'
    chassis_type = 'single_rp'
    state_machine_class = FxosFp4kStateMachine
    connection_provider_class = FxosConnectionProvider
    subcommand_list = FxosF4pkServiceList
    settings = FxosFp4kSettings()
