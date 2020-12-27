"""
Module:
    unicon.plugins.ironware

Author:
    James Di Trapani <james@ditrapani.com.au> - https://github.com/jamesditrapani

Description:
    This subpackage implements Ironware Support
"""

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.generic import GenericSingleRpConnectionProvider
from .statemachine import IronWareSingleRpStateMachine
from .services import IronWareServiceList
from .settings import IronWareSettings


class IronWareSingleRPConnection(BaseSingleRpConnection):
    os = 'ironware'
    chassis_type = 'single_rp'
    state_machine_class = IronWareSingleRpStateMachine
    connection_provider_class = GenericSingleRpConnectionProvider
    subcommand_list = IronWareServiceList
    settings = IronWareSettings()
