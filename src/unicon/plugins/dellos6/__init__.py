'''
Author: Knox Hutchinson
Contact: https://dataknox.dev
https://twitter.com/data_knox
https://youtube.com/c/dataknox
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.plugins.ios.iosv import IosvSingleRpConnection

from .statemachine import DellosSingleRpStateMachine
from .services import DellosServiceList
from .settings import DellosSettings


class DellosSingleRPConnection(IosvSingleRpConnection):
    '''DellosSingleRPConnection

    Dell OS6 platform support. Because our imaginary platform was inspired
    from Cisco IOSv platform, we are extending (inhering) from its plugin.
    '''
    os = 'dellos6'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = DellosSingleRpStateMachine
    subcommand_list = DellosServiceList
    settings = DellosSettings()
