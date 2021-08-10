__author__ = "dwapstra"

from .. import (IOSXRSingleRpConnection, IOSXRDualRpConnection,
                IOSXRSingleRpStateMachine, IOSXRSingleRpConnectionProvider,
                IOSXRDualRpConnection, IOSXRDualRpConnectionProvider)
from ..statemachine import (IOSXRSingleRpStateMachine,
                            IOSXRDualRpStateMachine)
from .. import (IOSXRSingleRpConnection, IOSXRDualRpConnection,
                IOSXRServiceList, IOSXRHAServiceList)

from . import service_implementation as ncs_svc

from .settings import NCS5KSettings


class Ncs5kServiceList(IOSXRServiceList):
    def __init__(self):
        super().__init__()
        self.reload = ncs_svc.Reload

class Ncs5kHAServiceList(IOSXRHAServiceList):
    """ Generic dual rp services. """
    def __init__(self):
        super().__init__()
        self.reload = ncs_svc.HAReload


class Ncs5kSingleRpConnection(IOSXRSingleRpConnection):
    os = 'iosxr'
    platform = 'ncs5k'
    chassis_type = 'single_rp'
    state_machine_class = IOSXRSingleRpStateMachine
    connection_provider_class = IOSXRSingleRpConnectionProvider
    subcommand_list = Ncs5kServiceList
    settings = NCS5KSettings()


class Ncs5kDualRpConnection(IOSXRDualRpConnection):
    os = 'iosxr'
    platform = 'ncs5k'
    chassis_type = 'dual_rp'
    state_machine_class = IOSXRDualRpStateMachine
    connection_provider_class = IOSXRDualRpConnectionProvider
    subcommand_list = Ncs5kHAServiceList
    settings = NCS5KSettings()
