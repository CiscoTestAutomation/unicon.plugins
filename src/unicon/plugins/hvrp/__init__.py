"""
Module:
    unicon.plugins.hvrp
Authors:
    Miguel Botia (mibotiaf@cisco.com), Leonardo Anez (leoanez@cisco.com)
Description:
    This subpackage implements Huawei VRP devices
"""

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.hvrp.connection_provider import HvrpSingleRpConnectionProvider
from .statemachine import HvrpSingleRpStateMachine
from unicon.plugins.hvrp.settings import HvrpSettings
from unicon.plugins.generic import ServiceList, service_implementation as gsvc
from unicon.plugins.hvrp import service_implementation as svc


class HvrpServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.send = svc.Send
        self.sendline = svc.Sendline
        self.expect = svc.Expect
        self.execute = svc.Execute
        self.configure = svc.Configure
        self.enable = svc.Enable
        self.disable = svc.Disable
        self.log_user = svc.LogUser
        self.bash_console = svc.BashService
        self.expect_log = gsvc.ExpectLogging


class HvrpSingleRpConnection(BaseSingleRpConnection):
    os = 'hvrp'
    platform = None
    chassis_type = 'single_rp'
    state_machine_class = HvrpSingleRpStateMachine
    connection_provider_class = HvrpSingleRpConnectionProvider
    subcommand_list = HvrpServiceList
    settings = HvrpSettings()
