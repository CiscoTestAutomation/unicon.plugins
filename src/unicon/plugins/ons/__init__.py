from unicon.plugins.generic import GenericSingleRpConnection
from unicon.plugins.generic import ServiceList

from .settings import OnsSettings
from .statemachine import OnsSingleRpStateMachine
from .connection_provider import OnsSingleRpConnectionProvider


class OnsServiceList(ServiceList):
    def __init__(self):
        super().__init__()


class OnsSingleRpConnection(GenericSingleRpConnection):
    os = 'ons'
    chassis_type = 'single_rp'
    state_machine_class = OnsSingleRpStateMachine
    connection_provider_class = OnsSingleRpConnectionProvider
    subcommand_list = OnsServiceList
    settings = OnsSettings()
