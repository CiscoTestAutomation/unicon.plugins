__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.plugins.generic.service_implementation import \
    Configure as GenericConfigure, \
    Execute as GenericExecute
from unicon.eal.dialogs import Dialog
from unicon.bases.routers.services import BaseService
from .service_statements import dest_file_startup

class Reload(BaseService):
    pass

class Shell(BaseService):
    pass

class Rommon(BaseService):
    pass

class Configure(GenericConfigure):
    def call_service(self, command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        super().call_service(command, reply=reply,
                             timeout=timeout, *args, **kwargs)


class Config(Configure):
    def call_service(self, command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        self.connection.log.warn('**** This service is deprecated. ' +
                                 'Please use "configure" service ****')
        super().call_service(command, reply=reply,
                             timeout=timeout, *args, **kwargs)


class Execute(GenericExecute):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog += Dialog([dest_file_startup])
