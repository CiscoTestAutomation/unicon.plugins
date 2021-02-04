__author__ = "Myles Dear <mdear@cisco.com>"


from unicon.plugins.ios import IosServiceList, IosSingleRpConnection
from unicon.plugins.ios.iosv import service_implementation as svc
from .statemachine import IosvSingleRpStateMachine
from .setting import IosvSettings


class IosvServiceList(IosServiceList):
    def __init__(self):
        super().__init__()
        self.reload = svc.Reload
        self.shellexec = svc.Shell
        self.config = svc.Config
        self.configure = svc.Configure
        self.execute = svc.Execute
        self.rommon = svc.Rommon


class IosvSingleRpConnection(IosSingleRpConnection):
    os = 'ios'
    platform = 'iosv'
    chassis_type = 'single_rp'
    state_machine_class = IosvSingleRpStateMachine
    subcommand_list = IosvServiceList
    settings = IosvSettings()
