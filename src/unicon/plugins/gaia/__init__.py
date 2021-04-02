'''
Author: Sam Johnson
Contact: samuel.johnson@gmail.com
https://github.com/TestingBytes

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider
from unicon.plugins.generic import GenericSingleRpConnection, ServiceList
from unicon.plugins.generic import service_implementation as svc
from unicon.plugins.linux import service_implementation as linux_svc
from unicon.plugins.gaia import service_implementation as gaia_svc
from unicon.plugins.gaia.statemachine import GaiaStateMachine
from unicon.plugins.gaia.settings import GaiaSettings

class GaiaConnectionProvider(GenericSingleRpConnectionProvider):
    pass

class GaiaServiceList(ServiceList):
    """ gaia services """
    def __init__(self):
        # super().__init__()
        
        self.execute = gaia_svc.GaiaExecute
        self.sendline = svc.Sendline
        self.ping = linux_svc.Ping
        self.traceroute = gaia_svc.GaiaTraceroute

class GaiaConnection(GenericSingleRpConnection):
    '''GaiaosSingleRPConnection

    Check Point Gaia platform support. 
    '''

    os = 'gaia'
    platform = None
    chassis_type = 'single_rp'
    state_machine_class = GaiaStateMachine
    connection_provider_class = GaiaConnectionProvider
    subcommand_list = GaiaServiceList
    settings = GaiaSettings()