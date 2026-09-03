from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine
from unicon.plugins.generic import ServiceList
from unicon.plugins.generic import GenericSingleRpConnectionProvider
from unicon.plugins.generic import service_implementation as gsvc

from unicon.plugins.iosxe.cat9k.c9800 import IosXEc9800ServiceList, IosXEc9800SingleRpConnection

from .settings import ApSettings
from . import service_implementation as svc
from .statemachine import IosXEEwcSingleRpStateMachine


class ApServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.execute = svc.Execute
        self.send = gsvc.Send
        self.sendline = gsvc.Sendline
        self.expect = gsvc.Expect
        self.enable = gsvc.Enable
        self.disable = gsvc.Disable
        self.reload = gsvc.Reload
        self.log_user = gsvc.LogUser
        self.bash_console = svc.IosXEEWCBashService
        self.ap_shell = svc.EWCApShellService


class IosXEEwcSingleRpConnection(IosXEc9800SingleRpConnection):
    os = 'iosxe'
    platform = 'cat9k'
    model = 'c9100ap'
    chassis_type = 'single_rp'
    subcommand_list = ApServiceList
    state_machine_class = IosXEEwcSingleRpStateMachine
    subcommand_list = ApServiceList
    settings = ApSettings()
