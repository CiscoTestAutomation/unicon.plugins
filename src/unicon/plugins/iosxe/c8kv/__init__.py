
from unicon.plugins.iosxe import IosXEServiceList, IosXESingleRpConnection
from unicon.plugins.iosxe.c8kv.statemachine import IosXEC8kvSingleRpStateMachine
from unicon.internal.plugins.iosxe.connection_provider import InternalIosxeSingleRpConnectionProvider

class IosXEC8kvServiceList(IosXEServiceList):
    def __init__(self):
        super().__init__()

class IosXEC8kvSingleRpConnection(IosXESingleRpConnection):
    platform = 'c8kv'
    os = 'iosxe'
    state_machine_class = IosXEC8kvSingleRpStateMachine
    connection_provider_class = InternalIosxeSingleRpConnectionProvider
    subcommand_list = IosXEC8kvServiceList
