__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.plugins.generic.settings import GenericSettings

class IosvSettings(GenericSettings):
    """ Timeouts for virtual platforms are increased to account for
    a busy execution server.
    """
    def __init__(self):
        super().__init__()
        self.CONNECTION_TIMEOUT = 480
        self.EXPECT_TIMEOUT = 60

        # Wait this much time between telnetting to the device and
        # hitting <Enter>.  Lack of a delay was causing connection timeouts
        # when running on a LaaS server in vCenter Esxi mode.
        #
        self.ESCAPE_CHAR_CALLBACK_PRE_SENDLINE_PAUSE_SEC = 1
