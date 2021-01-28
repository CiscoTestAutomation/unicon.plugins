""" NSO (Network Service Orchestrator) CLI implementation """

__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon.plugins.confd import ConfdConnection, ConfdServiceList, ConfdConnectionProvider
from unicon.plugins.confd.statemachine import ConfdStateMachine
from unicon.plugins.confd.settings import ConfdSettings


class NsoConnection(ConfdConnection):
    os = 'nso'
    platform = None
    chassis_type = 'single_rp'
    state_machine_class = ConfdStateMachine
    connection_provider_class = ConfdConnectionProvider
    subcommand_list = ConfdServiceList
    settings = ConfdSettings()

