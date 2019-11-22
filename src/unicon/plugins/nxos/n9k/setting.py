__author__ = 'Difu Hu <difhu@cisco.com>'

from unicon.plugins.nxos.setting import NxosSettings


class Nxos9kSettings(NxosSettings):

    def __init__(self):
        super().__init__()
        self.MAX_BOOT_ATTEMPTS = 3
