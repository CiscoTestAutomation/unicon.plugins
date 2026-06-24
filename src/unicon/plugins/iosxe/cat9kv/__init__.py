from unicon.plugins.iosxe import IosXEServiceList, IosXESingleRpConnection
from unicon.plugins.iosxe.cat9kv.statemachine import IosXECat9kvSingleRpStateMachine

from . import service_implementation as svc


class IosXECat9kvServiceList(IosXEServiceList):
    def __init__(self):
        super().__init__()
        self.reload = svc.Reload


class IosXECat9kvSingleRpConnection(IosXESingleRpConnection):
    platform = 'cat9kv'
    os = 'iosxe'
    state_machine_class = IosXECat9kvSingleRpStateMachine
    subcommand_list = IosXECat9kvServiceList
