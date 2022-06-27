"""
Module:
    unicon.plugins.junos

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    This module imports connection provider class which has
    exposes two methods named connect and disconnect. These
    methods are implemented in such a way so that they can
    handle majority of platforms and subclassing is seldom
    required.
"""
from unicon.bases.routers.connection_provider import BaseSingleRpConnectionProvider
from unicon.eal.dialogs import Dialog
from unicon.plugins.aos.statements import aosConnection_statement_list
from unicon.plugins.generic.statements import custom_auth_statements


class aosSingleRpConnectionProvider(BaseSingleRpConnectionProvider):
    """ Implements Junos singleRP Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to any device via generic implementation
    """
    def __init__(self, connecction, context, **kwargs):

        """ Initializes the generic connection provider
        """
        self.connection = connection
        self.context = context
        self.timeout_pattern = ['Timeout occurred', ]
        self.error_pattern = ["my command error"]
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.result = None
        self.__dict__.update(kwargs)

    def call_service(self, command,dialog=Dialog([]), *args, **kwargs):
        """ creates and returns a Dialog to handle all device prompts
            appearing during initial connection to the device.
            See statements.py for connnection statement lists
        """
        con = self.connection
        con.log.debug("+++ run_command +++")
        con.spawn.sendline(command)
        self.result = con.spawn.expect(.*#?)
        custom_auth_stmt = custom_auth_statements(
                             self.connection.settings.LOGIN_PROMPT,
                             self.connection.settings.PASSWORD_PROMPT)
        return con.connect_reply \
                    + Dialog(custom_auth_stmt + aosConnection_statement_list
                         if custom_auth_stmt else aosConnection_statement_list)
    def pre_service(self, *args, **kwargs):
        # Check if connection is established
        if self.connection.is_connected:
            return
        elif self.connection.reconnect:
            self.connection.connect()
        else:
            raise ConnectionError("Connection is not established to device")

        # Bring the device to required state to issue a command.
        self.connection.state_machine.go_to(self.start_state,
                                            self.connection.spawn,
                                            context=self.connection.context)

    def post_service(self, *args, **kwargs):
        # Bring the device back to end state which is disable
        self.connection.state_machine.go_to(self.end_state,
                                            self.connection.spawn,
                                            context=self.connection.context)

    def get_service_result(self):
        # Base class get_service will verify error and timeout pattern and return
        # self.result content if no error found.
        pass