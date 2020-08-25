"""
Module:
    unicon.plugins.junos

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    This subpackage implements Junos devices
"""
from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.junos.connection_provider import JunosSingleRpConnectionProvider
from .statemachine import JunosSingleRpStateMachine
from .setting import JunosSettings
from unicon.plugins.generic import ServiceList, service_implementation as gsvc
from unicon.plugins.junos import service_implementation as svc


class JunosServiceList(object):
    def __init__(self):
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


class JunosSingleRpConnection(BaseSingleRpConnection):
    os = 'junos'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = JunosSingleRpStateMachine
    connection_provider_class = JunosSingleRpConnectionProvider
    subcommand_list = JunosServiceList
    settings = JunosSettings()
