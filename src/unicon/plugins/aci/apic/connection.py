import warnings
from unicon.plugins.generic import GenericSingleRpConnection, service_implementation as svc
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider

from unicon.plugins.generic import ServiceList, service_implementation as svc
from unicon.eal.dialogs import Statement

from . import service_implementation as aci_svc
from .statemachine import AciStateMachine
from .settings import AciSettings


class AciApicConnectionProvider(GenericSingleRpConnectionProvider):
    """
        Connection provider class for aci connections.
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the generic connection provider
        """

        warnings.warn("This plugin aci/apic wil be deprecated, it has been moved"
            "to be a seperate plugin. Please set it in the testbed yaml file as "
            "follows:\nos: apic", DeprecationWarning)

        super().__init__(*args, **kwargs)

    def get_connection_dialog(self):
        dialog = super().get_connection_dialog()

        def update_state(con, state):
            con.state_machine.update_cur_state(state)

        con = self.connection
        state = con.state_machine.get_state('setup')
        dialog.append(Statement(pattern=state.pattern,
                      action=update_state,
                      args={'con': con, 'state': state.name}))
        return dialog

    def init_handle(self):
        con = self.connection
        con._is_connected = True
        if con.state_machine.current_state != 'setup':
            super().init_handle()



class AciApicServiceList(ServiceList):
    """ aci services. """

    def __init__(self):
        super().__init__()
        self.execute = aci_svc.Execute
        self.configure = svc.Configure
        self.reload = aci_svc.Reload


class AciApicConnection(GenericSingleRpConnection):
    """
        Connection class for aci connections.
    """

    os = 'aci'
    series = 'apic'
    chassis_type = 'single_rp'
    state_machine_class = AciStateMachine
    connection_provider_class = AciApicConnectionProvider
    subcommand_list = AciApicServiceList
    settings = AciSettings()