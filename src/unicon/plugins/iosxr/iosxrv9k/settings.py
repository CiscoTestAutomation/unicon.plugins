__author__ = "Syed Raza <syedraza@cisco.com>"

from unicon.plugins.iosxr.settings import IOSXRSettings

class IOSXRV9KSettings(IOSXRSettings):

    def __init__(self):
        """ Timeouts for virtual platforms are increased to account for
        a busy execution server.
        """
        super().__init__()
        # A Sunstone was seen to take 23 minutes or longer to come up
        # on a memory-overbooked server presumably thrashing to disk,
        # set this threshold to account for a busy server but don't
        # set so high as to accept a machine that is obviously running
        # too slowly to allow useful testing.
        self.INITIAL_LAUNCH_WAIT_SEC = 1200
        self.POST_PROMPT_WAIT_SEC = 110
        self.CONNECTION_TIMEOUT = 480
        self.EXPECT_TIMEOUT = 60
        self.INITIAL_LAUNCH_DISCOVERY_WAIT_SEC = 2

        # Wait this much time between telnetting to the device and
        # hitting <Enter>.  Lack of a delay was causing connection timeouts
        # when running on a LaaS server in vCenter Esxi mode.
        #
        self.ESCAPE_CHAR_CALLBACK_PRE_SENDLINE_PAUSE_SEC = 1
