__author__ = 'Difu Hu <pyats-support@cisco.com;pyats-support-ext@cisco.com>'

from unicon.bases.routers.connection_provider import BaseSingleRpConnectionProvider
from unicon.eal.dialogs import Dialog

from .statements import (sros_pre_connection_statement_list,
                         sros_auth_other_statement_list,
                         sros_auth_username_password_statement_list,
                         custom_auth_username_password_statements)


class SrosSingleRpConnectionProvider(BaseSingleRpConnectionProvider):

    def init_handle(self):
        con = self.connection
        con.state_machine.go_to(con.settings.DEFAULT_CLI_ENGINE,
                                con.spawn,
                                context=con.context,
                                prompt_recovery=self.prompt_recovery,
                                timeout=con.connection_timeout)
        self.execute_init_commands()

    def get_connection_dialog(self):
        con = self.connection
        custom_user_pw_stmt = custom_auth_username_password_statements(
            con.settings.LOGIN_PROMPT,
            con.settings.PASSWORD_PROMPT
        )
        return con.connect_reply \
               + Dialog(sros_pre_connection_statement_list
                        + sros_auth_other_statement_list
                        + custom_user_pw_stmt
                        + sros_auth_username_password_statement_list)

    def set_init_commands(self):
        con = self.connection

        self.init_exec_commands = []
        self.init_config_commands = []

        if con.init_exec_commands is not None:
            self.init_exec_commands = con.init_exec_commands
        else:
            if con.state_machine.current_state == 'mdcli':
                self.init_exec_commands = con.settings.MD_INIT_EXEC_COMMANDS
            elif con.state_machine.current_state == 'classiccli':
                self.init_exec_commands = con.settings.CLASSIC_INIT_EXEC_COMMANDS

        if con.init_config_commands is not None:
            self.init_config_commands = con.init_config_commands
        else:
            if con.state_machine.current_state == 'mdcli':
                self.init_config_commands = con.settings.MD_INIT_CONFIG_COMMANDS
            elif con.state_machine.current_state == 'classiccli':
                self.init_config_commands = con.settings.CLASSIC_INIT_CONFIG_COMMANDS
