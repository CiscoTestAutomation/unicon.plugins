__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"


from unicon_plugins.plugins.generic.service_implementation import \
    Execute as GenericExecute
from unicon.eal.dialogs import Dialog
from unicon_plugins.plugins.iosxe.service_statements import confirm


class Execute(GenericExecute):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog += Dialog([confirm])
