"""
Module:
    unicon.plugins.ironware

Author:
    James Di Trapani <james@ditrapani.com.au> - https://github.com/jamesditrapani

Description:
    * Base init to define Ironware NOS Support.
    * Defines custom service list.
"""

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.generic import GenericSingleRpConnectionProvider, \
                                    ServiceList

from .statemachine import IronWareSingleRpStateMachine
from .settings import IronWareSettings
from unicon.plugins.ironware import service_implementation

__author__ = 'James Di Trapani <james@ditrapani.com.au>'


class IronWareServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.execute = service_implementation.Execute
        self.mpls_ping = service_implementation.MPLSPing


class IronWareSingleRPConnection(BaseSingleRpConnection):
    os = 'ironware'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = IronWareSingleRpStateMachine
    connection_provider_class = GenericSingleRpConnectionProvider
    subcommand_list = IronWareServiceList
    settings = IronWareSettings()
