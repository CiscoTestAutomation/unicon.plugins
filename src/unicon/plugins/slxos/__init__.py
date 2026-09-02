"""
Module:
    unicon.plugins.slxos
Author:
    Fabio Pessoa Nunes (https://www.linkedin.com/in/fpessoanunes/)
Description:
    This subpackage implements Extreme SLX devices
"""

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.slxos.connection_provider import SlxosSingleRpConnectionProvider
from .statemachine import SlxosSingleRpStateMachine
from .settings import SlxosSettings
from unicon.plugins.generic import ServiceList
from unicon.plugins.slxos import service_implementation as svc


class SlxosServiceList(ServiceList):
    def __init__(self):
        super().__init__()
        self.send = svc.Send
        self.sendline = svc.Sendline
        self.expect = svc.Expect
        self.execute = svc.Execute
        self.configure = svc.Configure
        self.save = svc.Save
        self.copy = svc.Copy


class SlxosSingleRPConnection(BaseSingleRpConnection):
    '''SlxosSingleRPConnection
    Slxos platform support.
    '''
    os = 'slxos'
    chassis_type = 'single_rp'
    state_machine_class = SlxosSingleRpStateMachine
    connection_provider_class = SlxosSingleRpConnectionProvider
    subcommand_list = SlxosServiceList
    settings = SlxosSettings()
