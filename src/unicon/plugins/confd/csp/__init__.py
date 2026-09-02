__author__ = "Dave Wapstra <dwapstra@cisco.com>"


from unicon.plugins.confd import ConfdServiceList, ConfdConnection, ConfdConnectionProvider
from .statemachine import CspStateMachine
from .settings import CspSettings
from . import service_implementation as csp_svc


class CspServiceList(ConfdServiceList):
    def __init__(self):
        super().__init__()
        delattr(self, 'cli_style')
        self.reload = csp_svc.Reload


class CspSingleRPConnection(ConfdConnection):
    os = 'confd'
    platform = 'csp'
    chassis_type = 'single_rp'
    state_machine_class = CspStateMachine
    connection_provider_class = ConfdConnectionProvider
    subcommand_list = CspServiceList
    settings = CspSettings()
