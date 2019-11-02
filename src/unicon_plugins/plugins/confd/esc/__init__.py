__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon_plugins.plugins.confd import ConfdServiceList, ConfdConnection, ConfdConnectionProvider
from unicon_plugins.plugins.confd.statemachine import ConfdStateMachine
from unicon_plugins.plugins.confd.settings import ConfdSettings


class EscServiceList(ConfdServiceList):
    def __init__(self):
        super().__init__()
        delattr(self, 'cli_style')


class EscSingleRPConnection(ConfdConnection):
    os = 'confd'
    series = 'esc'
    chassis_type = 'single_rp'
    state_machine_class = ConfdStateMachine
    connection_provider_class = ConfdConnectionProvider
    subcommand_list = EscServiceList
    settings = ConfdSettings()
