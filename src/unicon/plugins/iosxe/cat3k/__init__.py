__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"


from .statemachine import IosXECat3kSingleRpStateMachine
from unicon.plugins.iosxe import IosXEServiceList, IosXESingleRpConnection
from unicon.plugins.iosxe.cat3k import service_implementation as svc
from .setting import IosXECat3kSettings


class IosXECat3kServiceList(IosXEServiceList):
    def __init__(self):
        super().__init__()
        self.reload = svc.Reload
        self.shellexec = svc.Shell
        self.rommon = svc.Rommon


class IosXECat3kSingleRpConnection(IosXESingleRpConnection):
    platform = 'cat3k'
    os = 'iosxe'
    chassis_type = 'single_rp'
    state_machine_class = IosXECat3kSingleRpStateMachine
    subcommand_list = IosXECat3kServiceList
    settings = IosXECat3kSettings()
