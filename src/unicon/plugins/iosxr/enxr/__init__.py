"""
An EnXR connection implementation.
"""

__author__ = "Ashok Joshi <ashojosh@cisco.com>"

from unicon.plugins.iosxr.enxr import service_implementation as svc
from unicon.plugins.generic import ServiceList
from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.iosxr.enxr.connection_provider \
    import IOSXREnxrSingleRpConnectionProvider
from unicon.plugins.iosxr.statemachine import IOSXRSingleRpStateMachine
from unicon.plugins.iosxr.settings import IOSXRSettings


class IOSXREnxrServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.execute = svc.Execute


class IOSXREnxrSingleRpConnection(BaseSingleRpConnection):
    os = 'iosxr'
    series = 'enxr'
    chassis_type = 'single_rp'
    state_machine_class = IOSXRSingleRpStateMachine
    connection_provider_class = IOSXREnxrSingleRpConnectionProvider
    subcommand_list = IOSXREnxrServiceList
    settings = IOSXRSettings()
