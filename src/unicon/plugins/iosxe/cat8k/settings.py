__author__ = "Lukas McClelland <lumcclel@cisco.com>"

from unicon.plugins.iosxe.settings import IosXESettings


class IosXECat8kSettings(IosXESettings):

    def __init__(self):
        super().__init__()
        self.POST_SWITCHOVER_WAIT = 30
