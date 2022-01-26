""" CAT4K IOS-XE Settings. """

from unicon.plugins.iosxe.settings import IosXESettings

class IosXECat4kSettings(IosXESettings):

    def __init__(self):
        super().__init__()
        self.CONNECTION_TIMEOUT=10
        self.RELOAD_TIMEOUT = 300
        self.CONNECTION_TIMEOUT = 300
        # prompt wait delay
        self.ESCAPE_CHAR_PROMPT_WAIT = 0.5
        # prompt wait retries
        # (wait time: 0.5, 1, 1.5 == total wait: 3s)
        self.ESCAPE_CHAR_PROMPT_WAIT_RETRIES = 3
