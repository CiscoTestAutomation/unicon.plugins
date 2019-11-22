__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.plugins.iosxr.settings import IOSXRSettings

class IOSXRVSettings(IOSXRSettings):

    def __init__(self):
        """ Timeouts for virtual platforms are increased to account for
        a busy execution server.
        """
        super().__init__()
        # When set to 900, saw an XRVR fail to come up
        # on a lightly loaded server.
        self.INITIAL_LAUNCH_WAIT_SEC = 1200

        # When set to 240 and 300, saw the following prompt in some cases
        # when initial config was attempted:
        # SYSTEM CONFIGURATION IS STILL IN PROGRESS Please do not attempt
        # to reconfigure the device until this process is complete.
        self.POST_PROMPT_WAIT_SEC = 420
        self.CONNECTION_TIMEOUT = 480
        self.EXPECT_TIMEOUT = 60
        self.EXEC_TIMEOUT = 120
        self.CONFIG_TIMEOUT = 60
        self.SLEEP_PRE_LAUNCH = 5

        # Wait this much time between telnetting to the device and
        # hitting <Enter>.  Lack of a delay was causing connection timeouts
        # when running on a LaaS server in vCenter Esxi mode.
        #
        self.ESCAPE_CHAR_CALLBACK_PRE_SENDLINE_PAUSE_SEC = 1
