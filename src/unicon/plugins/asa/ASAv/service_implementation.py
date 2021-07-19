from unicon.plugins.generic.service_implementation import Reload
from unicon.eal.dialogs import Dialog, Statement
from unicon.plugins.asa.ASAv.service_statements import asa_reload_stmt_list

class ASAReload(Reload):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.dialog = Dialog(asa_reload_stmt_list)
