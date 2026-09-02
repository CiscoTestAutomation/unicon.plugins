__author__ = "Myles Dear <mdear@cisco.com>"


from unicon.plugins.ios import IosServiceList, IosSingleRpConnection
from unicon.plugins.ios.settings import IosSettings
from .statemachine import IosPagentSingleRpStateMachine
from ..settings import IosSettings


class IosPagentServiceList(IosServiceList):
    def __init__(self):
        super().__init__()


class IosvSingleRpConnection(IosSingleRpConnection):
    os = 'ios'
    platform = 'pagent'
    chassis_type = 'single_rp'
    state_machine_class = IosPagentSingleRpStateMachine
    subcommand_list = IosPagentServiceList
    settings = IosSettings()
