"""
Module:
    unicon.plugins.linux

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    This subpackage implements Linux
"""

from unicon.bases.linux.connection import BaseLinuxConnection
from unicon.plugins.generic import service_implementation as svc

from unicon.plugins.linux import service_implementation as lnx_svc
from unicon.plugins.linux.connection_provider import LinuxConnectionProvider
from unicon.plugins.linux.settings import LinuxSettings
from unicon.plugins.linux.statemachine import LinuxStateMachine


class LinuxServiceList:
    """
    Linux services.
    """

    def __init__(self):
        self.send = svc.Send
        self.sendline = svc.Sendline
        self.transmit = svc.Send
        self.receive = svc.ReceiveService
        self.receive_buffer = svc.ReceiveBufferService
        self.expect = svc.Expect
        self.log_user = svc.LogUser
        self.execute = lnx_svc.Execute
        self.ping = lnx_svc.Ping
        self.expect_log = svc.ExpectLogging
        self.sudo = lnx_svc.Sudo


class LinuxConnection(BaseLinuxConnection):
    """
    Connection class for Linux connections.
    """
    os = 'linux'
    platform = None
    chassis_type = 'single_rp'
    # TODO Recheck this single_rp value for linux
    state_machine_class = LinuxStateMachine
    connection_provider_class = LinuxConnectionProvider
    subcommand_list = LinuxServiceList
    settings = LinuxSettings()
