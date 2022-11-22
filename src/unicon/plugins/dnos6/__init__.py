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
from .statemachine import Dnos6SingleRpStateMachine
from .services import Dnos6ServiceList
from .settings import Dnos6Settings


class Dnos6SingleRPConnection(BaseSingleRpConnection):
    '''Dnos6SingleRPConnection

    Dell OS6 PowerSwitch support.
    '''
    os = 'dnos6'
    chassis_type = 'single_rp'
    state_machine_class = Dnos6SingleRpStateMachine
    connection_provider_class = GenericSingleRpConnectionProvider
    subcommand_list = Dnos6ServiceList
    settings = Dnos6Settings()
