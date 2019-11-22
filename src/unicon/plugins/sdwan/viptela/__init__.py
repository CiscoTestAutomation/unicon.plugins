from unicon.eal.dialogs import Dialog, Statement
from unicon.plugins.confd import ConfdServiceList, ConfdConnection, ConfdConnectionProvider

from .settings import ViptelaSettings
from .statemachine import ViptelaStateMachine

from . import service_implementation as Viptela_svc


def console_session(spawn, context):
    context['console'] = True

connected_console_stmt = Statement(pattern=r"^(.*?)connected from .* using console",
                                   action=console_session,
                                   args=None,
                                   loop_continue=True,
                                   continue_timer=False)


class ViptelaConnectionProvider(ConfdConnectionProvider):
    """
        Connection provided class for ConfD connections.
    """
    def get_connection_dialog(self):
        connection_dialogs = super().get_connection_dialog()
        connection_dialogs += Dialog([connected_console_stmt])

        return connection_dialogs


class ViptelaServiceList(ConfdServiceList):
    def __init__(self):
        super().__init__()
        delattr(self, 'cli_style')
        self.reload = Viptela_svc.Reload


class ViptelaSingleRPConnection(ConfdConnection):
    os = 'sdwan'
    series = 'viptela'
    chassis_type = 'single_rp'
    state_machine_class = ViptelaStateMachine
    connection_provider_class = ViptelaConnectionProvider
    subcommand_list = ViptelaServiceList
    settings = ViptelaSettings()
