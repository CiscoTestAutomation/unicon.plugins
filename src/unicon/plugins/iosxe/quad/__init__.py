""" IOS-XE Quad connection implementation """
from unicon.bases.routers.connection import BaseQuadRpConnection
from unicon.bases.routers.connection_provider import BaseQuadRpConnectionProvider

from unicon.plugins.iosxe import HAIosXEServiceList

from .settings import IosXEQuadSettings
from .statemachine import IosXEQuadStateMachine
from .service_implementation import QuadGetRPState, QuadSwitchover, QuadReload


class IosXEQuadServiceList(HAIosXEServiceList):

    def __init__(self):
        super().__init__()
        self.get_rp_state = QuadGetRPState
        self.switchover = QuadSwitchover
        self.reload = QuadReload


class IosXEQuadRPConnection(BaseQuadRpConnection):
    os = 'iosxe'
    series = None
    chassis_type = 'quad'
    subcommand_list = IosXEQuadServiceList
    state_machine_class = IosXEQuadStateMachine
    connection_provider_class = BaseQuadRpConnectionProvider
    settings = IosXEQuadSettings()
