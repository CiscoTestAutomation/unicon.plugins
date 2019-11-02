
from unicon_plugins.plugins.iosxe import IosXESingleRpConnection, IosXEServiceList
from unicon_plugins.plugins.iosxe.sdwan.statemachine import SDWANSingleRpStateMachine 
from unicon_plugins.plugins.iosxe.sdwan import service_implementation as svc
from unicon_plugins.plugins.iosxe.sdwan.settings import SDWANSettings

class SDWANServiceList(IosXEServiceList):
    def __init__(self):
        super().__init__()
        self.configure = svc.SDWANConfigure

class SDWANSingleRpConnection(IosXESingleRpConnection):
    os = 'iosxe'
    series = 'sdwan'
    state_machine_class = SDWANSingleRpStateMachine
    subcommand_list = SDWANServiceList
    settings = SDWANSettings()
