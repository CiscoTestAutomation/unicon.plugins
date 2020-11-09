"""
An EnXR connection implementation.
"""

__author__ = "Ashok Joshi <ashojosh@cisco.com>"

from unicon.plugins.iosxr.enxr import service_implementation as svc
from unicon.plugins.generic import ServiceList
from unicon.bases.routers.connection import BaseSingleRpConnection
<<<<<<< HEAD
from unicon.plugins.iosxr.enxr.connection_provider import IOSXREnxrSingleRpConnectionProvider
from unicon.plugins.iosxr.statemachine import IOSXRSingleRpStateMachine
from unicon.plugins.iosxr.settings import IOSXRSettings

class IOSXREnxrServiceList(ServiceList):
=======
from unicon.plugins.iosxr.enxr.connection_provider import EnxrSingleRpConnectionProvider
from unicon.plugins.iosxr.statemachine import IOSXRSingleRpStateMachine
from unicon.plugins.iosxr.settings import IOSXRSettings


class EnxrServiceList(ServiceList):
>>>>>>> edcc7403ef1fc3ce709728b2c86e50dc54ee2453
    def __init__(self):
        super().__init__()
        self.execute = svc.Execute


<<<<<<< HEAD
class IOSXREnxrSingleRpConnection(BaseSingleRpConnection):
=======
class EnxrSingleRpConnection(BaseSingleRpConnection):
>>>>>>> edcc7403ef1fc3ce709728b2c86e50dc54ee2453
    os = 'iosxr'
    series = 'enxr'
    chassis_type = 'single_rp'
    state_machine_class = IOSXRSingleRpStateMachine
<<<<<<< HEAD
    connection_provider_class = IOSXREnxrSingleRpConnectionProvider
    subcommand_list = IOSXREnxrServiceList
    settings = IOSXRSettings()
=======
    connection_provider_class = EnxrSingleRpConnectionProvider
    subcommand_list = EnxrServiceList
    settings = IOSXRSettings()
>>>>>>> edcc7403ef1fc3ce709728b2c86e50dc54ee2453
