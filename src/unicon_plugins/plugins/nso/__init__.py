""" NSO (Network Service Orchestrator) CLI implementation """

__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon_plugins.plugins.confd import ConfdConnection, ConfdServiceList, ConfdConnectionProvider
from unicon_plugins.plugins.confd.statemachine import ConfdStateMachine
from unicon_plugins.plugins.confd.settings import ConfdSettings


class NsoConnection(ConfdConnection):
    os = 'nso'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = ConfdStateMachine
    connection_provider_class = ConfdConnectionProvider
    subcommand_list = ConfdServiceList
    settings = ConfdSettings()

