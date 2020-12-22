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
from .statemachine import DellSingleRpStateMachine
from .services import DellServiceList
from .settings import DellSettings


class DellSingleRPConnection(BaseSingleRpConnection):
    '''DellosSingleRPConnection

    Dell PowerSwitch platform support. Because our imaginary platform was inspired
    from Cisco IOSv platform, we are extending (inhering) from its plugin.
    '''
    os = 'dell'
    chassis_type = 'single_rp'
    state_machine_class = DellSingleRpStateMachine
    connection_provider_class = GenericSingleRpConnectionProvider
    subcommand_list = DellServiceList
    settings = DellSettings()
