from unicon.bases.routers.connection import BaseSingleRpConnection
from .statemachine import ASAStateMachine
from unicon.plugins.asa.provider import ASAConnectionProvider
from unicon.plugins.generic import ServiceList
from .settings import ASAvSettings
from .service_implementation import ASAReload

class ASAvServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.reload = ASAReload

class ASAvConnection(BaseSingleRpConnection):
    os = 'asa'
    series = 'asav'
    chassis_type = 'single_rp'
    state_machine_class = ASAStateMachine
    connection_provider_class = ASAConnectionProvider
    subcommand_list = ASAvServiceList
    settings = ASAvSettings()
