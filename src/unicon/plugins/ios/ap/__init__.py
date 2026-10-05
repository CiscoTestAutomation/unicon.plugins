__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"


from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine
from unicon.plugins.generic import ServiceList
from unicon.plugins.ios.ap.settings import ApSettings
from unicon.plugins.ios.connection_provider import IosSingleRpConnectionProvider
from unicon.plugins.ios.ap import service_implementation as svc


class ApServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.execute = svc.Execute


class ApSingleRpConnection(BaseSingleRpConnection):
    os = 'ios'
    platform = 'ap'
    chassis_type = 'single_rp'
    state_machine_class = GenericSingleRpStateMachine
    connection_provider_class = IosSingleRpConnectionProvider
    subcommand_list = ApServiceList
    settings = ApSettings()
