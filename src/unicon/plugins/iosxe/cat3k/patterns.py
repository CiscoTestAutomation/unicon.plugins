__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"

from unicon.plugins.iosxe.patterns import IosXEPatterns


class IosXECat3kPatterns(IosXEPatterns):
    def __init__(self):
        super().__init__()
        self.tcpdump = ".*listening on lfts.*$"
