
from unicon.plugins.iosxe.c9800 import IosXEc9800ServiceList, IosXEc9800SingleRpConnection

from . import service_implementation as svc
from .statemachine import IosXEEwcSingleRpStateMachine

class IosXEEwcServiceList(IosXEc9800ServiceList):
    def __init__(self):
        super().__init__()
        self.bash_console = svc.IosXEEWCBashService
        self.ap_shell = svc.EWCApShellService


class IosXEEwcSingleRpConnection(IosXEc9800SingleRpConnection):
    os = 'iosxe'
    platform = 'c9800'
    model = 'ewc_ap'
    chassis_type = 'single_rp'
    subcommand_list = IosXEEwcServiceList
    state_machine_class = IosXEEwcSingleRpStateMachine
