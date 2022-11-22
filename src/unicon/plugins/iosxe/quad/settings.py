""" IOS-XE Quad Settings """

from unicon.plugins.iosxe.settings import IosXESettings

class IosXEQuadSettings(IosXESettings):

    def __init__(self):
        super().__init__()

        # Quad detect rpr timeout
        self.DETECT_RPR_TIMEOUT = 1

        # Quad switchover timeout
        self.QUAD_SWITCHOVER_TIMEOUT = 600
        # Secs to sleep after switchover
        self.QUAD_SWITCHOVER_SLEEP = 30

        # Quad reload timeout
        self.QUAD_RELOAD_TIMEOUT = 600
        # Secs to sleep after reload
        self.QUAD_RELOAD_SLEEP = 60
