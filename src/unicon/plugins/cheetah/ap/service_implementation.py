__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"


from unicon.plugins.generic.service_implementation import \
    Execute as GenericExecute
from unicon.plugins.generic.service_implementation import \
    Reload as GenericReload
from unicon.eal.dialogs import Dialog
from unicon.plugins.iosxe.service_statements import confirm

from .service_statement import ap_reload_list

class Execute(GenericExecute):
    def call_service(self, command=None, reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        command = list() if command is None else command
        super().call_service(command,
                             reply=reply + Dialog([confirm,]),
                             timeout=timeout, *args, **kwargs)
        
class Reload(GenericReload):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog = self.dialog + Dialog(ap_reload_list)