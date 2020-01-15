__author__ = 'Difu Hu <pyats-support@cisco.com;pyats-support-ext@cisco.com>'

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.generic import service_implementation as svc

from .connection_provider import SrosSingleRpConnectionProvider
from .statemachine import SrosSingleRpStateMachine
from .setting import SrosSettings
from . import service_implementation as sros_svc


class SrosServiceList(object):
    def __init__(self):
        self.send = svc.Send
        self.sendline = svc.Sendline
        self.expect = svc.Expect
        self.expect_log = svc.ExpectLogging
        self.log_user = svc.LogUser
        self.log_file = svc.LogFile
        self.mdcli_execute = sros_svc.SrosMdcliExecute
        self.mdcli_configure = sros_svc.SrosMdcliConfigure
        self.classic_execute = sros_svc.SrosClassicExecute
        self.classic_configure = sros_svc.SrosClassicConfigure


class SrosSingleRpConnection(BaseSingleRpConnection):
    os = 'sros'
    chassis_type = 'single_rp'
    state_machine_class = SrosSingleRpStateMachine
    connection_provider_class = SrosSingleRpConnectionProvider
    subcommand_list = SrosServiceList
    settings = SrosSettings()
