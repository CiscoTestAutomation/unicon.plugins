from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider

from . import statements

from unicon.eal.dialogs import Dialog


class ASAConnectionProvider(GenericSingleRpConnectionProvider):

    def get_connection_dialog(self):
        dialog = super().get_connection_dialog()
        dialog += Dialog([statements.bad_password_stmt])
        return dialog
