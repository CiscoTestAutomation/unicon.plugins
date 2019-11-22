__author__ = 'Difu Hu <difhu@cisco.com>'

from unicon.plugins.iosxe.csr1000v import IosXECsr1000vServiceList, \
    IosXECsr1000vSingleRpConnection
from .service_implementation import IosXECsr1000vVewlcCopy


class IosXECsr1000vVewlcServiceList(IosXECsr1000vServiceList):
    def __init__(self):
        super().__init__()
        self.copy = IosXECsr1000vVewlcCopy


class IosXECsr1000vVewlcSingleRpConnection(IosXECsr1000vSingleRpConnection):
    model = 'vewlc'
    subcommand_list = IosXECsr1000vVewlcServiceList
