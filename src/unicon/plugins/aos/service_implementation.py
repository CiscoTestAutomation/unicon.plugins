from unicon.plugins.generic.service_implementation import \
    Configure as GenericConfigure, \
    Execute as GenericExecute
from unicon.eal.dialogs import Dialog
from unicon.bases.routers.services import BaseService
from unicon.plugins.generic.service_implementation import BashService, \
                                                          Send, Sendline, \
                                                          Expect, Execute, \
                                                          Configure ,\
                                                          Enable, Disable, \
                                                          LogUser
from unicon.eal.dialogs import Dialog

class Configure(Configure):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'config'
        self.end_state = 'enable'
        self.service_name = 'config'