__copyright__ = "# Copyright (c) 2018 by cisco Systems, Inc. All rights reserved."
__author__ = "dwapstra"

from unicon.plugins.generic import GenericSingleRpConnection, service_implementation as svc
from unicon.plugins.generic.connection_provider import GenericSingleRpConnectionProvider

from unicon.plugins.generic import ServiceList, service_implementation as svc
from . import service_implementation as windows_svc
from .statemachine import WindowsStateMachine
from .settings import WindowsSettings


class WindowsConnectionProvider(GenericSingleRpConnectionProvider):
    """
        Connection provider class for windows connections.
    """

    def init_handle(self):
        con = self.connection
        con._is_connected = True


class WindowsServiceList(ServiceList):
    """ windows services. """

    def __init__(self):
        super().__init__()
        self.execute = windows_svc.Execute


class WindowsConnection(GenericSingleRpConnection):
    """
        Connection class for windows connections.
    """
    os = 'windows'
    series = None
    chassis_type = 'single_rp'
    state_machine_class = WindowsStateMachine
    connection_provider_class = WindowsConnectionProvider
    subcommand_list = WindowsServiceList
    settings = WindowsSettings()
