from unicon.bases.linux.connection_provider import BaseLinuxConnectionProvider
from unicon.eal.dialogs import Dialog

from .statements import (linux_pre_connection_statement_list,
                         linux_auth_other_statement_list,
                         linux_auth_username_password_statement_list,
                         custom_auth_username_password_statements)


class LinuxConnectionProvider(BaseLinuxConnectionProvider):
    """
    Connection provided class for Linux connections.
    """

    def get_connection_dialog(self):
        con = self.connection
        custom_user_pw_stmt = custom_auth_username_password_statements(
            self.connection.settings.LOGIN_PROMPT,
            self.connection.settings.PASSWORD_PROMPT
        )
        return con.connect_reply \
                      + Dialog(linux_pre_connection_statement_list
                      + linux_auth_other_statement_list
                      + custom_user_pw_stmt
                      + linux_auth_username_password_statement_list)
