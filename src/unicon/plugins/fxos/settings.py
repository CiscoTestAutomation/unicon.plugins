""" Defines the settings for fxos based unicon connections """

__author__ = "dwapstra"

from unicon.plugins.generic.settings import GenericSettings


class FxosSettings(GenericSettings):
    """" Generic platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()

        self.HA_INIT_EXEC_COMMANDS = []
        self.HA_INIT_CONFIG_COMMANDS = []

        self.TERM = 'vt100'
        self.ERROR_PATTERN = [
            r'ERROR: % Invalid input detected',
            r'^Error:',
            r'^%\s*[Ii]nvalid [Cc]ommand',
            r"^%\s*Ambiguous command at '\^' marker",
            r'^.*\x07'
        ]

        # Increasing the expect timeout since its used for go_to state transitions
        # The transition to diagnostic CLI take take 10+ seconds due to in-use session
        self.EXPECT_TIMEOUT = 15

        self.RELOAD_WAIT = 420
        self.RELOAD_RECONNECT_ATTEMPTS = 3
        self.POST_RELOAD_WAIT = 60

        self.BOOT_TIMEOUT = 600

        # What pattern to wait for after system restart
        self.BOOT_WAIT_PATTERN = r'^.*User enable_1 logged in to'
        # How many times the boot_wait_msg should occur to determine boot has finished
        self.BOOT_WAIT_PATTERN_COUNT = 1
