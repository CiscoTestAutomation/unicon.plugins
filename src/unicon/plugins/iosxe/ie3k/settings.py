from unicon.plugins.iosxe.settings import IosXESettings


class IosXEIe3kSettings(IosXESettings):

    def __init__(self):
        super().__init__()

        self.BOOT_FILESYSTEM = ["flash:", "sdflash:"]
        self.BOOT_FILE_REGEX = [r'(\S+\.SSA\.bin)', r'(\S+\.SPA\.bin)', r'(\S+\.bin)']
