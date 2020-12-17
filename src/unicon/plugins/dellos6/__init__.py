'''
Author: Knox Hutchinson
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

# import the base dependencies
# (extending built-in plugins)

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

    # all subcommands (eg, connection methods) are called services, and are
    # listed under the ServiceList class. The ServiceList class aggregates all
    # services (classes) that implements the actual methods into one top-level
    # location, to be managed by the connection class.
    subcommand_list = DellosServiceList

    # any key/value setting pairs goes here
    settings = DellosSettings()
