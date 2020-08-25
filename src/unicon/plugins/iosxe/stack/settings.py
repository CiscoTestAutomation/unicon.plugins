""" Stack IOS-XE Settings. """

from unicon.plugins.iosxe.settings import IosXESettings

class IosXEStackSettings(IosXESettings):

    def __init__(self):
        super().__init__()

        # Switchover service timeout
        self.STACK_SWITCHOVER_TIMEOUT = 600
        # Secs to sleep after switchover
        self.STACK_SWITCHOVER_SLEEP = 120

        # Secs to sleep after reload
        self.STACK_POST_RELOAD_SLEEP = 180
        # Secs to sleep before booting device
        self.STACK_ROMMON_SLEEP = 20
        # Stack reload timeout
        self.STACK_RELOAD_TIMEOUT = 900

