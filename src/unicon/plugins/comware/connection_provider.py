'''
Author: Renato Almeida de Oliveira
Contact: renato.almeida.oliveira@gmail.com
https://twitter.com/ORenato_Almeida
https://www.youtube.com/c/RenatoAlmeidadeOliveira
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.bases.routers.connection_provider import BaseSingleRpConnectionProvider
from unicon.plugins.generic.statements import custom_auth_statements, connection_statement_list
from unicon.eal.dialogs import Dialog
from unicon.plugins.comware.patterns import HPComwarePatterns

patterns = HPComwarePatterns()


class HPComwareSingleRpConnectionProvider(BaseSingleRpConnectionProvider):
    """ Implements Generic singleRP Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to any device via generic implementation
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the generic connection provider
        """
        super().__init__(*args, **kwargs)

    def get_connection_dialog(self):
        """ creates and returns a Dialog to handle all device prompts
            appearing during initial connection to the device.
            See statements.py for connnection statement lists
        """
        con = self.connection
        custom_auth_stmt = custom_auth_statements(
                             patterns.login_prompt,
                             patterns.password)
        return con.connect_reply + \
                    Dialog(custom_auth_stmt + connection_statement_list
                        if custom_auth_stmt else connection_statement_list)

