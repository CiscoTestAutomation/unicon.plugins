__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"

from unicon.plugins.iosxe.settings import IosXESettings


class IosXECat3kSettings(IosXESettings):

    def __init__(self):
        super().__init__()
        self.RELOAD_TIMEOUT = 600
        self.CONNECTION_TIMEOUT = 600  # Big timeout to handle transition rommon->enable
        self.STATE_TRANSITION_TIMEOUT = 30

        self.BOOT_FILESYSTEM = 'flash:'
