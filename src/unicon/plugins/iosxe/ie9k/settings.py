from unicon.plugins.iosxe.settings import IosXESettings


class IosXEIe9kSettings(IosXESettings):

    def __init__(self):
        super().__init__()

        self.EMERGENCY_FILESYSTEMS = ["emgy:", "emgy0:"]
        self.EMERGENCY_IMAGE_PATTERN = r'(\d+)\s+(\S+\.bin)'
        self.USE_RECOVERY_IMAGE_ON_RELOAD = True
        self.MAX_BOOT_ATTEMPTS = 5
        self.BOOT_FILESYSTEM = ["flash:", "sdflash:"]
        self.BOOT_FILE_REGEX = [
            r'(\S+\.SSA\.bin)',
            r'(\S+\.SPA\.bin)',
            r'(\S+\.bin)',
        ]
