__author__ = "Isobel Ormiston <iormisto@cisco.com>"

import time

from random import randint

from unicon.plugins.iosxr.connection_provider \
    import IOSXRSingleRpConnectionProvider, IOSXRDualRpConnectionProvider
from unicon.plugins.iosxr.moonshine.statements import MoonshineStatements
from unicon.plugins.iosxr.moonshine.patterns import MoonshinePatterns
from unicon.plugins.iosxr.errors import RpNotRunningError
from unicon.eal.dialogs import Dialog


patterns = MoonshinePatterns()
iosxr_statements = MoonshineStatements()

class MoonshineSingleRpConnectionProvider(IOSXRSingleRpConnectionProvider):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_init_commands(self):
        con = self.connection

        if con.init_exec_commands is not None:
            self.init_exec_commands = con.init_exec_commands
        else:
            self.init_exec_commands = []

        if con.init_config_commands is not None:
            self.init_config_commands = con.init_config_commands
        else:
            self.init_config_commands = []

    def init_handle(self):
        """ Executes the init commands on the device after bringing
            it to enable state """
        con = self.connection
        con.state_machine.go_to('enable',
                                self.connection.spawn,
                                context=self.connection.context,
                                timeout=self.connection.connection_timeout)
        self.execute_init_commands()


class MoonshineDualRpConnectionProvider(IOSXRDualRpConnectionProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_init_commands(self):
        con = self.connection

        if con.init_exec_commands is not None:
            self.init_exec_commands = con.init_exec_commands
        else:
            self.init_exec_commands = con.settings.IOSXR_INIT_EXEC_COMMANDS

        if con.init_config_commands is not None:
            self.init_config_commands = con.init_config_commands
        else:
            hostname_command = []
            if con.hostname != None and con.hostname != '':
                hostname_command = ['hostname ' + con.hostname]
            self.init_config_commands = hostname_command + con.settings.MOONSHINE_INIT_CONFIG_COMMANDS

