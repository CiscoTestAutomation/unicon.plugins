
from unicon.plugins.iosxe.settings import IosXESettings


class IosXECat9kSettings(IosXESettings):

    def __init__(self):
        super().__init__()
        self.FIND_BOOT_IMAGE = False
        self.BOOT_TIMEOUT = 420
        self.CONTAINER_EXIT_CMDS = ['exit\r', '\x03', '\x03', '\x03']
