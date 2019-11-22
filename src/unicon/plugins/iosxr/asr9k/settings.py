from unicon.plugins.iosxr.settings import IOSXRSettings


class IOSXRAsr9kSettings(IOSXRSettings):

    def __init__(self):
        super().__init__()
        self.STANDBY_STATE_REGEX = r'Standby node .* is (.*)'
