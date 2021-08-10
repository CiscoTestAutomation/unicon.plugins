"""
Module:
    unicon.plugins.nxos

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    This subpackage implements NXOS
"""
from unicon.bases.routers.connection import (BaseSingleRpConnection,
   BaseDualRpConnection)

from .connection_provider import NxosSingleRpConnectionProvider
from .connection_provider import NxosDualRpConnectionProvider

from .statemachine import NxosDualRpStateMachine

from .statemachine import NxosSingleRpStateMachine
from .setting import NxosSettings

from unicon.plugins.generic import ServiceList, HAServiceList
from unicon.plugins.nxos import service_implementation as svc


class NxosServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.reload = svc.Reload
        self.ping6 = svc.Ping6
        self.copy = svc.NxosCopy
        self.shellexec = svc.ShellExec
        self.list_vdc = svc.ListVdc
        self.switchto = svc.SwitchVdc
        self.switchback = svc.SwitchbackVdc
        self.create_vdc = svc.CreateVdc
        self.delete_vdc = svc.DeleteVdc
        self.attach_console = svc.AttachModuleConsole
        self.bash_console = svc.BashService
        self.configure = svc.Configure
        self.configure_dual = svc.ConfigureDual
        self.execute = svc.NxosExecute


class HANxosServiceList(HAServiceList):
    def __init__(self):
        super().__init__()
        self.get_rp_state = svc.GetRPState
        self.get_mode = svc.GetMode
        self.copy = svc.NxosCopy
        self.reload = svc.HANxosReloadService
        self.switchover = svc.NxosSwitchoverService
        self.reset_standby_rp = svc.ResetStandbyRP
        self.shellexec = svc.HAShellExec
        self.list_vdc = svc.ListVdc
        self.switchto = svc.SwitchVdc
        self.switchback = svc.SwitchbackVdc
        self.create_vdc = svc.CreateVdc
        self.delete_vdc = svc.DeleteVdc
        self.attach_console = svc.AttachModuleConsole
        self.bash_console = svc.BashService
        self.ping6 = svc.Ping6
        self.configure = svc.Configure


class NxosSingleRpConnection(BaseSingleRpConnection):
    os = 'nxos'
    platform = None
    chassis_type = 'single_rp'
    state_machine_class = NxosSingleRpStateMachine
    connection_provider_class = NxosSingleRpConnectionProvider
    subcommand_list = NxosServiceList
    settings = NxosSettings()


class NxosDualRPConnection(BaseDualRpConnection):
    os = 'nxos'
    platform = None
    chassis_type = 'dual_rp'
    state_machine_class = NxosDualRpStateMachine
    connection_provider_class = NxosDualRpConnectionProvider
    subcommand_list = HANxosServiceList
    settings = NxosSettings()
