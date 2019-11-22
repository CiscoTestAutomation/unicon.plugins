__author__ = 'Difu Hu <difhu@cisco.com>'

from unicon.plugins.iosxe.cat3k import IosXECat3kServiceList, \
    IosXECat3kSingleRpConnection
from .service_implementation import IosXECat3kEwlcCopy


class IosXECat3kEwlcServiceList(IosXECat3kServiceList):
    def __init__(self):
        super().__init__()
        self.copy = IosXECat3kEwlcCopy


class IosXECat3kEwlcSingleRpConnection(IosXECat3kSingleRpConnection):
    model = 'ewlc'
    subcommand_list = IosXECat3kEwlcServiceList
