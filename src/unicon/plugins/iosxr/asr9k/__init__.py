__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.plugins.iosxr import (IOSXRSingleRpConnection,
                                  IOSXRDualRpConnection)

from unicon.plugins.iosxr.asr9k.statemachine import (IOSXRASR9KSingleRpStateMachine,
                                                     IOSXRASR9KDualRpStateMachine)
from unicon.plugins.iosxr import (IOSXRServiceList,
                                  IOSXRHAServiceList)

from unicon.plugins.iosxr.connection_provider import (IOSXRSingleRpConnectionProvider,
                                                      IOSXRDualRpConnectionProvider)
from . import service_implementation as asr9k_svc 
from unicon.plugins.iosxr.asr9k.settings import IOSXRAsr9kSettings


class IOSXRASR9KServiceList(IOSXRServiceList):
    def __init__(self):
        super().__init__()
        self.reload = asr9k_svc.Reload


class IOSXRASR9KHAServiceList(IOSXRHAServiceList):
    def __init__(self):
        super().__init__()
        self.reload = asr9k_svc.HAReload


class IOSXRASR9KSingleRpConnection(IOSXRSingleRpConnection):
    os = 'iosxr'
    platform = 'asr9k'
    chassis_type = 'single_rp'
    state_machine_class = IOSXRASR9KSingleRpStateMachine
    connection_provider_class = IOSXRSingleRpConnectionProvider
    subcommand_list = IOSXRASR9KServiceList
    settings = IOSXRAsr9kSettings()


class IOSXRASR9KDualRpConnection(IOSXRDualRpConnection):
    os = 'iosxr'
    platform = 'asr9k'
    chassis_type = 'dual_rp'
    state_machine_class = IOSXRASR9KDualRpStateMachine
    connection_provider_class = IOSXRDualRpConnectionProvider
    subcommand_list = IOSXRASR9KHAServiceList
    settings = IOSXRAsr9kSettings()
