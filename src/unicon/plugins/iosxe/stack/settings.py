""" Stack IOS-XE Settings. """

from unicon.plugins.iosxe.settings import IosXESettings

class IosXEStackSettings(IosXESettings):

    def __init__(self):
        super().__init__()

        # Switchover service timeout
        self.STACK_SWITCHOVER_TIMEOUT = 600
        # Switchover postcheck interval
        self.SWITCHOVER_POSTCHECK_INTERVAL = 30
        self.POST_SWITCHOVER_SLEEP = 90

        # Secs to sleep before reconnect device
        self.STACK_POST_RELOAD_SLEEP = 30
        # Secs to sleep before booting device
        self.STACK_ROMMON_SLEEP = 20
        # Stack reload timeout
        self.STACK_RELOAD_TIMEOUT = 900
        # Reload postcheck interval
        self.RELOAD_POSTCHECK_INTERVAL = 30

