"""
Module:
    unicon.plugins.hvrp
Authors:
    Miguel Botia (mibotiaf@cisco.com), Leonardo Anez (leoanez@cisco.com)
Description:
    This Module implements two methods for conection and disconnection for HVRP devices.
"""

from time import sleep
from unicon.bases.routers.connection_provider import \
    BaseSingleRpConnectionProvider
from unicon.eal.dialogs import Dialog
from .statements import connection_statement_list
from unicon.plugins.generic.statements import custom_auth_statements


class HvrpSingleRpConnectionProvider(BaseSingleRpConnectionProvider):
    """ Implements Hvrp singleRP Connection Provider,
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
            self.connection.settings.LOGIN_PROMPT,
            self.connection.settings.PASSWORD_PROMPT)
        return con.connect_reply \
               + Dialog(custom_auth_stmt + connection_statement_list
                        if custom_auth_stmt else connection_statement_list)

    def disconnect(self):
        """ Logout and disconnect from the device
        """
        con = self.connection
        if con.connected:
            con.log.info('Disconnecting...')
            con.sendline('quit')
            sleep(2)
            con.expect('.*')
            con.log.info('Closing connection...')
            con.spawn.close()
