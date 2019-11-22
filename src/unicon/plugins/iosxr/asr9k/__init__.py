__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.bases.routers.connection import BaseDualRpConnection

from unicon.plugins.iosxr.asr9k.statemachine import IOSXRASR9KSingleRpStateMachine
from unicon.plugins.iosxr.asr9k.statemachine import IOSXRASR9KDualRpStateMachine
from unicon.plugins.iosxr.__init__ import IOSXRServiceList
from unicon.plugins.iosxr.__init__ import IOSXRHAServiceList

from unicon.plugins.iosxr.connection_provider \
    import IOSXRSingleRpConnectionProvider
from unicon.plugins.iosxr.connection_provider \
    import IOSXRDualRpConnectionProvider
from unicon.plugins.iosxr.asr9k.settings import IOSXRAsr9kSettings


class IOSXRASR9KSingleRpConnection(BaseSingleRpConnection):
    os = 'iosxr'
    series = 'asr9k'
    chassis_type = 'single_rp'
    state_machine_class = IOSXRASR9KSingleRpStateMachine
    connection_provider_class = IOSXRSingleRpConnectionProvider
    subcommand_list = IOSXRServiceList
    settings = IOSXRAsr9kSettings()


class IOSXRASR9KDualRpConnection(BaseDualRpConnection):
    os = 'iosxr'
    series = 'asr9k'
    chassis_type = 'dual_rp'
    state_machine_class = IOSXRASR9KDualRpStateMachine
    connection_provider_class = IOSXRDualRpConnectionProvider
    subcommand_list = IOSXRHAServiceList
    settings = IOSXRAsr9kSettings()
