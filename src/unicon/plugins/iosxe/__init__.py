""" A generic IOS-XE connection implementation.
It covers many IOS-XE platforms, including ASR and ISR.
 """

__author__ = "Myles Dear <pyats-support@cisco.com>"


from unicon.plugins.generic import ServiceList, HAServiceList
from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.iosxe.statemachine import IosXESingleRpStateMachine
from unicon.plugins.iosxe.statemachine import IosXEDualRpStateMachine
from unicon.plugins.generic import GenericSingleRpConnectionProvider,\
    GenericDualRPConnection
from unicon.plugins.iosxe.settings import IosXESettings

from unicon.plugins.iosxe import service_implementation as svc


class IosXEServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.config = svc.Config
        self.configure = svc.Configure
        self.execute = svc.Execute
        self.ping = svc.Ping
        self.traceroute = svc.Traceroute
        self.bash_console = svc.BashService
        self.copy = svc.Copy
        self.reload = svc.Reload
        self.rommon = svc.Rommon
        self.tclsh = svc.Tclsh


class HAIosXEServiceList(HAServiceList):
    def __init__(self):
        super().__init__()

        self.config = svc.HAConfig
        self.configure = svc.HAConfigure
        self.execute = svc.HAExecute
        self.reload = svc.HAReload
        self.switchover = svc.HASwitchover
        self.ping = svc.Ping
        self.bash_console = svc.BashService
        self.traceroute = svc.Traceroute
        self.copy = svc.Copy
        self.reset_standby_rp = svc.ResetStandbyRP
        self.rommon = svc.HARommon
        self.tclsh = svc.Tclsh


class IosXESingleRpConnection(BaseSingleRpConnection):
    os = 'iosxe'
    platform = None
    chassis_type = 'single_rp'
    state_machine_class = IosXESingleRpStateMachine
    connection_provider_class = GenericSingleRpConnectionProvider
    subcommand_list = IosXEServiceList
    settings = IosXESettings()


class IosXEDualRPConnection(GenericDualRPConnection):
    os = 'iosxe'
    platform = None
    chassis_type = 'dual_rp'
    subcommand_list = HAIosXEServiceList
    state_machine_class = IosXEDualRpStateMachine
    settings = IosXESettings()
