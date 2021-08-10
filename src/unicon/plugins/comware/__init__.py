'''
Author: Renato Almeida de Oliveira
Contact: renato.almeida.oliveira@gmail.com
https://twitter.com/ORenato_Almeida
https://www.youtube.com/c/RenatoAlmeidadeOliveira
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.generic import ServiceList

from unicon.plugins.comware.statemachine import HPComwareSingleRpStateMachine
from unicon.plugins.comware.connection_provider import HPComwareSingleRpConnectionProvider
from unicon.plugins.comware import service_implementation as svc
from unicon.plugins.comware.settings import HPSettings


class HPComwareServiceList(ServiceList):
    '''HP Comware Service List
    '''

    def __init__(self):
        super().__init__()
        self.execute = svc.HPExecute
        self.configure = svc.HPConfigure
        self.save = svc.HPSave
        self.ping = svc.HPComwarePing
        self.traceroute = svc.HPComwareTraceroute


class HPComwareSingleRPConnection(BaseSingleRpConnection):
    '''HPComwareSingleRPConnection

    HP Comware platform support.
    '''
    os = 'comware'
    chassis_type = 'single_rp'
    state_machine_class = HPComwareSingleRpStateMachine
    connection_provider_class = HPComwareSingleRpConnectionProvider
    subcommand_list = HPComwareServiceList
    settings = HPSettings()

