from unicon.eal.dialogs import Dialog, Statement
from unicon_plugins.plugins.confd import ConfdServiceList, ConfdConnection, ConfdConnectionProvider

from .settings import SDWANSettings
from .statemachine import SDWANStateMachine

from . import service_implementation as sdwan_svc


def console_session(spawn, context):
    context['console'] = True

connected_console_stmt = Statement(pattern=r"^(.*?)connected from .* using console",
                                   action=console_session,
                                   args=None,
                                   loop_continue=True,
                                   continue_timer=False)


class SDWANConnectionProvider(ConfdConnectionProvider):
    """
        Connection provided class for ConfD connections.
    """
    def get_connection_dialog(self):
        connection_dialogs = super().get_connection_dialog()
        connection_dialogs += Dialog([connected_console_stmt])

        return connection_dialogs


class SDWANServiceList(ConfdServiceList):
    def __init__(self):
        super().__init__()
        delattr(self, 'cli_style')
        self.reload = sdwan_svc.Reload


class SDWANSingleRPConnection(ConfdConnection):
    os = 'sdwan'
    chassis_type = 'single_rp'
    state_machine_class = SDWANStateMachine
    connection_provider_class = SDWANConnectionProvider
    subcommand_list = SDWANServiceList
    settings = SDWANSettings()
