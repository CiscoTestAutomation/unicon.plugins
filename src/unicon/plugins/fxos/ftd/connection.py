import warnings
from time import sleep
from unicon.plugins.generic import GenericSingleRpConnection, ServiceList
from unicon.eal.dialogs import Dialog

from .. import FxosConnectionProvider
from . import service_implementation as ftd_svc
from .statemachine import FtdStateMachine
from .statements import FtdStatements
from .settings import FtdSettings


ftd_statements = FtdStatements()


class FtdConnectionProvider(FxosConnectionProvider):
    """
        Connection provider class for fxos connections.
    """

    def __init__(self, *args, **kwargs):
        """ Initializes the connection provider
        """
        warnings.warn("This plugin fxos/ftd is deprecated, it has been"
                      "replaced by fxos, fxos/fp4k and fxos/fp9k."
                      "Please update your topology file.",
                      DeprecationWarning)

        super().__init__(*args, **kwargs)

    def get_connection_dialog(self):
        dialog = Dialog([ftd_statements.cssp_stmt,
                         ftd_statements.command_not_completed_stmt])
        dialog += super().get_connection_dialog()
        return dialog

    def init_handle(self):
        con = self.connection
        self.execute_init_commands()

    def disconnect(self):
        """ Logout and disconnect from the device
        """
        con = self.connection
        if con.connected:
            con.log.info('Disconnecting...')
            if con.context.get('_ssh_session', False):
                if con.state_machine.current_state != 'module_console':
                    con.switchto('module_console')
            else:
                if con.state_machine.current_state != 'chassis':
                    con.switchto('chassis')
            con.sendline('exit')
            sleep(2)
            con.expect('.*')
            con.log.info('Closing connection...')
            con.spawn.close()


class FtdServiceList(ServiceList):
    """ fxos services. """

    def __init__(self):
        super().__init__()
        self.switchto = ftd_svc.Switchto


class FtdConnection(GenericSingleRpConnection):
    """
        Connection class for fxos connections.
    """
    os = 'fxos'
    platform = 'ftd'
    chassis_type = 'single_rp'
    state_machine_class = FtdStateMachine
    connection_provider_class = FtdConnectionProvider
    subcommand_list = FtdServiceList
    settings = FtdSettings()

