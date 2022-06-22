'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.generic import GenericSingleRpConnectionProvider
from .statemachine import aosSingleRpStateMachine
from .services import aosServiceList
from .settings import aosSettings


class aosSingleRPConnection(BaseSingleRpConnection):
    '''aosSingleRPConnection

    This supports logging into an Aruba switch.
    '''
    os = 'aos'
    chassis_type = 'single_rp'
    state_machine_class = aosSingleRpStateMachine
    connection_provider_class = GenericSingleRpConnectionProvider
    subcommand_list = aosServiceList
    settings = aosSettings()
