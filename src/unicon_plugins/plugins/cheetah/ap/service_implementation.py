__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"


from unicon_plugins.plugins.generic.service_implementation import \
    Execute as GenericExecute
from unicon.eal.dialogs import Dialog
from unicon_plugins.plugins.iosxe.service_statements import confirm


class Execute(GenericExecute):
    def call_service(self, command=None, reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        command = list() if command is None else command
        super().call_service(command,
                             reply=reply + Dialog([confirm,]),
                             timeout=timeout, *args, **kwargs)
