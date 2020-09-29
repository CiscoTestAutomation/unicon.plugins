from unicon.bases.routers.connection import BaseSingleRpConnection
from .statemachine import ASAStateMachine
from .provider import ASAConnectionProvider
from unicon.plugins.generic import ServiceList
from .settings import ASASettings
from .service_implementation import ASAExecute, ASAReload

class ASAServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.execute = ASAExecute
        self.reload = ASAReload

class ASAConnection(BaseSingleRpConnection):
    os = 'asa'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = ASAStateMachine
    connection_provider_class = ASAConnectionProvider
    subcommand_list = ASAServiceList
    settings = ASASettings()
