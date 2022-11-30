
from unicon.plugins.iosxe import IosXESingleRpConnection, IosXEServiceList, IosXEDualRPConnection
from unicon.plugins.iosxe.sdwan.statemachine import SDWANSingleRpStateMachine, SDWANDualRpStateMachine
from unicon.plugins.iosxe.sdwan import service_implementation as svc
from unicon.plugins.iosxe.sdwan.settings import SDWANSettings

class SDWANServiceList(IosXEServiceList):
    def __init__(self):
        super().__init__()
        self.configure = svc.SDWANConfigure

class SDWANSingleRpConnection(IosXESingleRpConnection):
    os = 'iosxe'
    platform = 'sdwan'
    state_machine_class = SDWANSingleRpStateMachine
    subcommand_list = SDWANServiceList
    settings = SDWANSettings()

class SDWANDualRpConnection(IosXEDualRPConnection):
    os = 'iosxe'
    platform = 'sdwan'
    state_machine_class = SDWANDualRpStateMachine
    subcommand_list = SDWANServiceList
    settings = SDWANSettings()
