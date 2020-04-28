
from unicon.plugins.generic import ServiceList, GenericSingleRpConnection, GenericDualRPConnection
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider

from .settings import AireosAPSettings
from .statemachine import AireosAPStateMachine


class AireosAPConnection(GenericSingleRpConnection):
    os = 'aireos'
    series = 'ap'
    chassis_type = 'single_rp'
    state_machine_class = AireosAPStateMachine
    connection_provider_class = GenericSingleRpConnectionProvider
    subcommand_list = ServiceList
    settings = AireosAPSettings()
