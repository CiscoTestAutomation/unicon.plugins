""" A Stack IOS-XE connection implementation.
"""

from unicon.plugins.generic import HAServiceList
from unicon.bases.routers.connection import BaseStackRpConnection
from .statemachine import StackIosXEStateMachine
from .settings import IosXEStackSettings
from unicon.bases.routers.connection_provider import BaseStackRpConnectionProvider
from unicon.plugins.iosxe import service_implementation as svc
from .service_implementation import StackGetRPState, StackSwitchover, StackReload

class StackIosXEServiceList(HAServiceList):
    def __init__(self):
        super().__init__()
        self.config = svc.HAConfig
        self.configure = svc.HAConfigure
        self.execute = svc.HAExecute
        self.reload = StackReload
        self.switchover = StackSwitchover
        self.get_rp_state = StackGetRPState


class IosXEStackRPConnection(BaseStackRpConnection):
    os = 'iosxe'
    series = None
    chassis_type = 'stack'
    subcommand_list = StackIosXEServiceList
    state_machine_class = StackIosXEStateMachine
    connection_provider_class = BaseStackRpConnectionProvider
    settings = IosXEStackSettings()
