from unicon.bases.routers.connection import BaseSingleRpConnection
from .statemachine import ASAStateMachine
from .provider import ASAConnectionProvider
from unicon.plugins.generic import ServiceList
from .settings import ASASettings

class ASAConnection(BaseSingleRpConnection):
    os = 'asa'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = ASAStateMachine
    connection_provider_class = ASAConnectionProvider
    subcommand_list = ServiceList
    settings = ASASettings()
