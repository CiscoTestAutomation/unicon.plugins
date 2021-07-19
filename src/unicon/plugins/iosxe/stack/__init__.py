""" A Stack IOS-XE connection implementation.
"""

from unicon.plugins.generic import HAServiceList
from unicon.plugins.iosxe import service_implementation as svc
from unicon.bases.routers.connection import BaseStackRpConnection

from .settings import IosXEStackSettings
from .statemachine import StackIosXEStateMachine
from .connection_provider import StackRpConnectionProvider
from .service_implementation import StackGetRPState, StackSwitchover, StackReload

class StackIosXEServiceList(HAServiceList):
    def __init__(self):
        super().__init__()
        self.ping = svc.Ping
        self.config = svc.HAConfig
        self.configure = svc.HAConfigure
        self.execute = svc.HAExecute
        self.reload = StackReload
        self.switchover = StackSwitchover
        self.get_rp_state = StackGetRPState


class IosXEStackRPConnection(BaseStackRpConnection):
    os = 'iosxe'
    platform = None
    chassis_type = 'stack'
    subcommand_list = StackIosXEServiceList
    state_machine_class = StackIosXEStateMachine
    connection_provider_class = StackRpConnectionProvider
    settings = IosXEStackSettings()
