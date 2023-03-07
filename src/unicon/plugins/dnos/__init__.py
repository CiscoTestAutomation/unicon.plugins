'''
Unicon Plugin Example Implementation
------------------------------------

In this example, we will implement a sample Unicon connection plugin supporting
the DRIVENETS platform named "dnos" by inheriting from the built-in Unicon
Base connection plugin.

Note:
    Make sure the content of this file contains the Connection subclass
    this plugin implements. 

'''

# import the base dependencies
# (extending built-in plugins)

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.generic import GenericSingleRpConnectionProvider
from unicon.plugins.dnos.statemachine import DnosSingleRpStateMachine
from unicon.plugins.dnos.services import DnosServiceList
from unicon.plugins.dnos.settings import DnosSettings
from unicon.plugins.generic import ServiceList


class DnosSingleRPConnection(BaseSingleRpConnection):
    '''DnosSingleRPConnection
    
    DRIVENETS dnos platform support. 
    '''

    # each connection plugin needs to declare the os it supports
    os = 'dnos'

    # there's no specific series in this platform
    # set it to None to indicate so
    series = None

    # single-rp chasis or dual-rp chasis
    chassis_type = 'single_rp'

    # each connection class must be accompanied by its own state machine class
    # a state machine class provides the connection implementation the means of
    # recognizing the current state the device is in, all available subsequent
    # states, and how to switch between states. (eg, from exec -> config)
    state_machine_class = DnosSingleRpStateMachine
    connection_provider_class = GenericSingleRpConnectionProvider

    # all subcommands (eg, connection methods) are called services, and are
    # listed under the ServiceList class. The ServiceList class aggregates all
    # services (classes) that implements the actual methods into one top-level
    # location, to be managed by the connection class.
    subcommand_list = DnosServiceList

    # any key/value setting pairs goes here
    settings = DnosSettings()


class DnosServiceList(ServiceList):
    '''
    class aggregating all service lists for this platform
    '''

    def __init__(self):
        # use the parent services
        super().__init__()
        # overwrite and add our own
        self.execute = Execute
        