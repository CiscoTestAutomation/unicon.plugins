__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.bases.routers.connection import BaseDualRpConnection

from unicon_plugins.plugins.iosxr.iosxrv.statemachine import IOSXRVSingleRpStateMachine
from unicon_plugins.plugins.iosxr.iosxrv.statemachine import IOSXRVDualRpStateMachine
from unicon_plugins.plugins.iosxr.__init__ import IOSXRServiceList
from unicon_plugins.plugins.iosxr.__init__ import IOSXRHAServiceList

from unicon_plugins.plugins.iosxr.iosxrv.connection_provider \
    import IOSXRVSingleRpConnectionProvider
from unicon_plugins.plugins.iosxr.iosxrv.connection_provider \
    import IOSXRVDualRpConnectionProvider
from unicon_plugins.plugins.iosxr.iosxrv.settings import IOSXRVSettings

class IOSXRVSingleRpConnection(BaseSingleRpConnection):
    os = 'iosxr'
    series = 'iosxrv'
    chassis_type = 'single_rp'
    state_machine_class = IOSXRVSingleRpStateMachine
    connection_provider_class = IOSXRVSingleRpConnectionProvider
    subcommand_list = IOSXRServiceList
    settings = IOSXRVSettings()

class IOSXRVDualRpConnection(BaseDualRpConnection):
    os = 'iosxr'
    series = 'iosxrv'
    chassis_type = 'dual_rp'
    state_machine_class = IOSXRVDualRpStateMachine
    connection_provider_class = IOSXRVDualRpConnectionProvider
    subcommand_list = IOSXRHAServiceList
    settings = IOSXRVSettings()
