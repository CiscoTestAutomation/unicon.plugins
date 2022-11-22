'''
Author: Knox Hutchinson
Contact: https://dataknox.dev
https://twitter.com/data_knox
https://youtube.com/c/dataknox
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.generic import GenericSingleRpConnectionProvider
from .statemachine import Dnos10SingleRpStateMachine
from .services import Dnos10ServiceList
from .settings import Dnos10Settings


class Dnos10SingleRPConnection(BaseSingleRpConnection):
    '''Dnos10SingleRPConnection

    Dell OS10 PowerSwitch support
    '''
    os = 'dnos10'
    chassis_type = 'single_rp'
    state_machine_class = Dnos10SingleRpStateMachine
    connection_provider_class = GenericSingleRpConnectionProvider
    subcommand_list = Dnos10ServiceList
    settings = Dnos10Settings()
