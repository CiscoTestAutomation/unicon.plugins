__author__ = 'Difu Hu <pyats-support@cisco.com;pyats-support-ext@cisco.com>'

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.generic import service_implementation as svc

from .connection_provider import TimosSingleRpConnectionProvider
from .statemachine import TimosSingleRpStateMachine
from .setting import TimosSettings
from . import service_implementation as timos_svc


class TimosServiceList(object):
    def __init__(self):
        self.send = svc.Send
        self.sendline = svc.Sendline
        self.expect = svc.Expect
        self.expect_log = svc.ExpectLogging
        self.log_user = svc.LogUser
        self.log_file = svc.LogFile
        self.execute = timos_svc.TimosExecute
        self.configure = timos_svc.TimosConfigure
        self.classic_execute = timos_svc.TimosClassicExecute
        self.classic_configure = timos_svc.TimosClassicConfigure


class TimosSingleRpConnection(BaseSingleRpConnection):
    os = 'timos'
    chassis_type = 'single_rp'
    state_machine_class = TimosSingleRpStateMachine
    connection_provider_class = TimosSingleRpConnectionProvider
    subcommand_list = TimosServiceList
    settings = TimosSettings()
