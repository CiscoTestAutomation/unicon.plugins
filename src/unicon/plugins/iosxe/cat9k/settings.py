
from unicon.plugins.iosxe.settings import IosXESettings


class IosXECat9kSettings(IosXESettings):

    def __init__(self):
        super().__init__()
        self.FIND_BOOT_IMAGE = False
