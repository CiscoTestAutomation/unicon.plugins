"""
Module:
    unicon.plugins.ise

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    This subpackage implements Ise
"""

import time

from unicon.bases.linux.connection import BaseLinuxConnection
from unicon.bases.linux.connection_provider import BaseLinuxConnectionProvider
from unicon.eal.dialogs import Dialog
from unicon.plugins.ise.patterns import IsePatterns
from unicon.plugins.ise.statemachine import IseStateMachine
from unicon.plugins.linux.settings import LinuxSettings
from unicon.plugins.ise import service_implementation as ise_svc
from unicon.plugins.generic import service_implementation as svc
from unicon.plugins.linux.statements import password_handler, username_handler

p = IsePatterns()

class IseSettings(LinuxSettings):
    def __init__(self):
        super().__init__()
        self.LINUX_INIT_EXEC_COMMANDS = []

def send_enter(spawn):
    time.sleep(2)
    spawn.sendline()

def more_handler(spawn):
    time.sleep(0.1)
    spawn.sendline('q')

def wait_and_send_yes(spawn):
    time.sleep(0.1)
    spawn.sendline('yes')

def permission_denied(spawn):
    """ handles connection refused scenarios
    """
    raise Exception('Permission denied for device "%s"' % (str(spawn),))

def connection_refused(spawn):
    """ handles connection refused scenarios
    """
    raise Exception('Connection refused to device "%s"' % (str(spawn),))

class IseConnectionProvider(BaseLinuxConnectionProvider):
    """
        Connection provided class for Ise connections.
    """
    def get_connection_dialog(self):
        con = self.connection
        return con.connect_reply + Dialog([
            [p.continue_connect,
                wait_and_send_yes,
                None, True, False],
            [p.permission_denied,
                permission_denied,
                None, False, False],
            [p.username,
                username_handler,
                None, True, False],
            [p.password,
                password_handler,
                None, True, False],
            [p.connection_refused,
                connection_refused,
                None, False, False],
            [p.reuse_session,
                send_enter,
                None, True, False],
            [p.more_prompt,
                more_handler,
                None, True, False],
            [p.enter_to_continue,
                send_enter,
                None, True, False],
            [p.escape_char,
                send_enter,
                None, True, False]
        ])

class IseServiceList:
    """ Linux services. """

    def __init__(self):
        self.send = svc.Send
        self.sendline = svc.Sendline
        self.expect = svc.Expect
        self.log_user = svc.LogUser
        self.execute = ise_svc.Execute
        self.configure = ise_svc.Configure
        self.expect_log = svc.ExpectLogging


class IseConnection(BaseLinuxConnection):
    """
        Connection class for Ise connections.
    """
    os = 'ise'
    platform = None
    chassis_type = 'single_rp'
    state_machine_class = IseStateMachine
    connection_provider_class = IseConnectionProvider
    subcommand_list = IseServiceList
    settings = IseSettings()

    def disconnect(self):
        """provides mechanism to disconnect to the device by
        duck typing connection provider's disconnect method
        """
        self.spawn.sendline('exit')
        self.spawn.close()
