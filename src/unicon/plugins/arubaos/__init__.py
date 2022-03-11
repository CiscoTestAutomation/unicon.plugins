'''
Author: Yannick Koehler
Contact: yannick@koehler.name
'''
from unicon.plugins.generic import ServiceList
from unicon.plugins.ios.iosv import IosvSingleRpConnection
from unicon.plugins.arubaos import service_implementation as svc

from .statemachine import ArubaosSingleRpStateMachine
from .settings import ArubaosSettings


class ArubaosServiceList(ServiceList):

    def __init__(self):
        # use the parent servies
        super().__init__()
        self.enable = svc.Enable
        self.disable = svc.Disable
        self.config = svc.Config
        self.rommon = svc.Rommon
        self.shell = svc.Shell
        self.switchto = svc.Switchto


class ArubaosSingleRPConnection(IosvSingleRpConnection):
    os = 'arubaos'
    platform = None
    chassis_type = 'single_rp'
    state_machine_class = ArubaosSingleRpStateMachine
    subcommand_list = ArubaosServiceList
    settings = ArubaosSettings()
