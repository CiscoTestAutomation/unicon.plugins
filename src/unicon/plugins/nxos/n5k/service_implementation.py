from unicon.plugins.nxos.service_implementation import Reload as BaseReload
from unicon.eal.dialogs import Dialog
from .service_statements import nxos_reload_statement_list

class Reload(BaseReload):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog = Dialog(nxos_reload_statement_list)
