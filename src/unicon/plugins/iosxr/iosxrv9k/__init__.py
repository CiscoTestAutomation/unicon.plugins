__author__ = "Syed Raza <syedraza@cisco.com>"

from unicon.plugins.iosxr.iosxrv9k.settings import IOSXRV9KSettings
from unicon.plugins.iosxr.statemachine import IOSXRSingleRpStateMachine
from unicon.plugins.iosxr.__init__ import IOSXRServiceList
from unicon.plugins.iosxr.iosxrv9k.connection_provider import IOSXRV9KSingleRpConnectionProvider
from unicon.bases.routers.connection import BaseSingleRpConnection

class IOSXRV9KSingleRpConnection(BaseSingleRpConnection):
    os = 'iosxr'
    series = 'iosxrv9k'
    chassis_type = 'single_rp'
    state_machine_class = IOSXRSingleRpStateMachine
    connection_provider_class = IOSXRV9KSingleRpConnectionProvider
    subcommand_list = IOSXRServiceList
    settings = IOSXRV9KSettings()
