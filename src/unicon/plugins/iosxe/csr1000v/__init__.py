__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.plugins.iosxe import IosXEServiceList, IosXESingleRpConnection

from .settings import IosXECsr1000vSettings
from .statemachine import IosXECsr1000vSingleRpStateMachine


class IosXECsr1000vServiceList(IosXEServiceList):
    pass


class IosXECsr1000vSingleRpConnection(IosXESingleRpConnection):
    series = 'csr1000v'
    state_machine_class = IosXECsr1000vSingleRpStateMachine
    subcommand_list = IosXECsr1000vServiceList
    settings = IosXECsr1000vSettings()
