"""
An EnXR connection implementation.
"""

__author__ = "Ashok Joshi <ashojosh@cisco.com>"

from unicon.plugins.iosxr.enxr import service_implementation as svc
from unicon.plugins.generic import ServiceList
from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.iosxr.enxr.connection_provider import EnxrSingleRpConnectionProvider
from unicon.plugins.iosxr.statemachine import IOSXRSingleRpStateMachine
from unicon.plugins.iosxr.settings import IOSXRSettings


class EnxrServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.execute = svc.Execute


class EnxrSingleRpConnection(BaseSingleRpConnection):
    os = 'iosxr'
    series = 'enxr'
    chassis_type = 'single_rp'
    state_machine_class = IOSXRSingleRpStateMachine
    connection_provider_class = EnxrSingleRpConnectionProvider
    subcommand_list = EnxrServiceList
    settings = IOSXRSettings()