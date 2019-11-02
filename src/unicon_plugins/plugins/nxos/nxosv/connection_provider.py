from unicon.eal.dialogs import Dialog

from unicon_plugins.plugins.nxos.connection_provider\
    import NxosSingleRpConnectionProvider

from unicon_plugins.plugins.nxos.nxosv.service_statements\
    import additional_connection_dialog

class NxosvSingleRpConnectionProvider(NxosSingleRpConnectionProvider):

    def get_connection_dialog(self):
        dialog = super().get_connection_dialog()
        dialog += Dialog(additional_connection_dialog)
        return dialog

