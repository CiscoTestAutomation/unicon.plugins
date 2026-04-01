from unicon.plugins.iosxe.settings import IosXESettings


class IosXEIe3kSettings(IosXESettings):

    def __init__(self):
        super().__init__()

        self.BOOT_FILESYSTEM = ["sdflash:", "flash:"]
