"""
Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)
"""

from unicon.eal.dialogs import Dialog
from unicon.bases.routers.connection_provider import BaseStackRpConnectionProvider

from unicon.plugins.generic.statements import connection_statement_list, custom_auth_statements


class StackRpConnectionProvider(BaseStackRpConnectionProvider):
    """ Implements Stack Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to stack device
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the base connection provider
        """
        super().__init__(*args, **kwargs)

    def get_connection_dialog(self):
        """ creates and returns a Dialog to handle all device prompts
            appearing during initial connection to the device.
            See generic/statements.py for connnection statement lists
        """
        con = self.connection
        custom_auth_stmt = custom_auth_statements(
                             self.connection.settings.LOGIN_PROMPT,
                             self.connection.settings.PASSWORD_PROMPT)
        return con.connect_reply + \
                    Dialog(custom_auth_stmt + connection_statement_list
                        if custom_auth_stmt else connection_statement_list)
