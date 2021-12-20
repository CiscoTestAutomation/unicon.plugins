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
            r'^%\s*[Aa]mbiguous (command|input)',
            r'% Bad IP address or host name',
            r'% Unknown command or computer name, or unable to find computer address'
        ]
        self.CONFIGURE_ERROR_PATTERN = [
            r'^%\s*[Ii]nvalid (command|input|number)',
            r'routing table \S+ does not exist'
        ]

        self.EXECUTE_MATCHED_RETRIES = 1
        self.EXECUTE_MATCHED_RETRY_SLEEP = 0.1

        self.CONFIG_LOCK_RETRY_SLEEP = 30
        self.CONFIG_LOCK_RETRIES = 10

        self.BOOT_TIMEOUT = 600

        self.FIND_BOOT_IMAGE = True
        self.MAX_BOOT_ATTEMPTS = 3
        self.BOOT_FILESYSTEM = 'bootflash:'
        self.BOOT_FILE_REGEX = r'(\S+\.bin)'

        self.SERVICE_PROMPT_CONFIG_CMD = 'service prompt config'
        self.CONFIG_PROMPT_WAIT = 2

        self.GUESTSHELL_CONFIG_CMDS = ['iox', 'app-hosting appid guestshell', 'app-vnic management guest-interface 0']
        self.GUESTSHELL_CONFIG_VERIFY_CMDS = ['show iox-service', 'show app-hosting list']
        self.GUESTSHELL_CONFIG_VERIFY_PATTERN = r'guestshell\s+RUNNING'
        self.GUESTSHELL_ENABLE_CMDS = 'guestshell enable'
        self.GUESTSHELL_ENABLE_VERIFY_CMDS = []
        self.GUESTSHELL_ENABLE_VERIFY_PATTERN = r''
