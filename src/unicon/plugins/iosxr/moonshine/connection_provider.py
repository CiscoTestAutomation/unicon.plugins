__author__ = "Isobel Ormiston <iormisto@cisco.com>"

import time

from random import randint

from unicon.plugins.iosxr.connection_provider import (
    IOSXRSingleRpConnectionProvider,
    IOSXRDualRpConnectionProvider,
    _INITIAL_CONNECTION,
    _RECOVERY_CONTEXT_KEYS,
    _recover_configuration_inconsistency,
)
from unicon.plugins.iosxr.moonshine.statements import MoonshineStatements
from unicon.plugins.iosxr.moonshine.patterns import MoonshinePatterns
from unicon.plugins.iosxr.errors import RpNotRunningError
from unicon.eal.dialogs import Dialog
from unicon.plugins.generic.connection_provider import GenericDualRpConnectionProvider


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


class MoonshineDualRpConnectionProvider(GenericDualRpConnectionProvider):
    # This class inherits from GenericDualRpConnectionProvider instead
    # of IOSXRDualRpConnectionProvider because we want to use the
    # generic `designate_handles` method.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def designate_handles(self):
        subconnections = self.connection.subconnections
        # Moonshine deliberately uses generic HA designation, bypassing the
        # IOS XR dual-RP provider that normally scopes this recovery context.
        # Apply it only while generic designation normalizes initial states so
        # later configuration transitions retain their existing commit policy.
        for subconnection in subconnections:
            subconnection.context[_INITIAL_CONNECTION] = True

        try:
            super().designate_handles()
            for subconnection in subconnections:
                _recover_configuration_inconsistency(
                    subconnection,
                    prompt_recovery=self.prompt_recovery,
                )
        finally:
            for subconnection in subconnections:
                for key in _RECOVERY_CONTEXT_KEYS:
                    subconnection.context.pop(key, None)

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

    def unlock_standby(self):
        pass

    def assign_ha_mode(self):
        pass
