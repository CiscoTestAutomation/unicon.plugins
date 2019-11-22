""" Generic IOS-XE Settings. """

__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.plugins.generic.settings import GenericSettings

class IosXESettings(GenericSettings):

    def __init__(self):
        super().__init__()

        # A single cycle of retries wasn't enough to recover an iosxe device
        # just rebooted after a "write erase".
        self.PROMPT_RECOVERY_RETRIES = 2
        self.ERROR_PATTERN = [
            r'^%\s*[Ii]nvalid (command|input)',
            r'^%\s*[Ii]ncomplete (command|input)',
            r'^%\s*[Aa]mbiguous (command|input)'
        ]

        self.EXECUTE_MATCHED_RETRIES = 1
        self.EXECUTE_MATCHED_RETRY_SLEEP = 0.1
