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
from .statemachine import Dellos6SingleRpStateMachine
from .services import Dellos6ServiceList
from .settings import Dellos6Settings


class Dellos6SingleRPConnection(BaseSingleRpConnection):
    '''DellosSingleRPConnection

    Dell OS6 platform support. Because our imaginary platform was inspired
    from Cisco IOSv platform, we are extending (inhering) from its plugin.
    '''
    os = 'dellos6'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = Dellos6SingleRpStateMachine
    connection_provider_class = GenericSingleRpConnectionProvider
    subcommand_list = Dellos6ServiceList
    settings = Dellos6Settings()
