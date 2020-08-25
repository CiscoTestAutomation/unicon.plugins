__author__ = 'Difu Hu <pyats-support@cisco.com;pyats-support-ext@cisco.com>'

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.generic import service_implementation as svc

from . import service_implementation as sros_svc
from .connection_provider import SrosSingleRpConnectionProvider
from .setting import SrosSettings
from .statemachine import SrosSingleRpStateMachine


class SrosServiceList(object):
    def __init__(self):
        self.send = svc.Send
        self.sendline = svc.Sendline
        self.expect = svc.Expect
        self.log_user = svc.LogUser
        self.log_file = svc.LogFile
        self.mdcli_execute = sros_svc.SrosMdcliExecute
        self.mdcli_configure = sros_svc.SrosMdcliConfigure
        self.classiccli_execute = sros_svc.SrosClassiccliExecute
        self.classiccli_configure = sros_svc.SrosClassiccliConfigure
        self.execute = sros_svc.SrosExecute
        self.configure = sros_svc.SrosConfigure
        self.switch_cli_engine = sros_svc.SrosSwitchCliEngine
        self.get_cli_engine = sros_svc.SrosGetCliEngine
        self.expect_log = svc.ExpectLogging


class SrosSingleRpConnection(BaseSingleRpConnection):
    os = 'sros'
    chassis_type = 'single_rp'
    state_machine_class = SrosSingleRpStateMachine
    connection_provider_class = SrosSingleRpConnectionProvider
    subcommand_list = SrosServiceList
    settings = SrosSettings()
