__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.plugins.iosxe.settings import IosXESettings


class IosXECsr1000vSettings(IosXESettings):
    def __init__(self):
        super().__init__()
        self.EXPECT_TIMEOUT = 60
        self.EXEC_TIMEOUT = 120
        self.CONFIG_TIMEOUT = 60

        # Wait this much time between telnetting to the device and
        # hitting <Enter>.  Lack of a delay was causing connection timeouts
        # against some image versions.
        self.ESCAPE_CHAR_CALLBACK_PRE_SENDLINE_PAUSE_SEC = 1

# This class name was changed.   Maintain the legacy name as well.
Csr1000vSettings = IosXECsr1000vSettings
