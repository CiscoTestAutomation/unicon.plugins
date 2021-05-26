'''
Author: Richard Day
Contact: https://www.linkedin.com/in/richardday/, https://github.com/rich-day

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.generic import GenericSingleRpConnectionProvider
from .statemachine import EOSSingleRpStateMachine
from .services import EOSServiceList
from .settings import EOSSettings

class EOSSingleRPConnection(BaseSingleRpConnection):
    '''
    Support for Arista EOS platform
    '''
    os = 'eos'
    platform = None
    chassis_type = 'single_rp'
    state_machine_class = EOSSingleRpStateMachine
    subcommand_list = EOSServiceList
    settings = EOSSettings()
    connection_provider_class = GenericSingleRpConnectionProvider
