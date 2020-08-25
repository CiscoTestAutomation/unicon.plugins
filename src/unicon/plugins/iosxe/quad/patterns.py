""" IOS-XE Quad Patterns """
from unicon.plugins.iosxe.patterns import IosXEPatterns


class IosXEQuadPatterns(IosXEPatterns):
    def __init__(self):
        super().__init__()

        self.rpr_state = r'RPR Mode: Remote supervisor is already active'
        self.unlock_state = r'RPR Mode: Remote Supervisor is no longer active'
        self.autoboot =r'Preparing to autoboot.+\[Press Ctrl-C to interrupt\]'
        self.ica = r'RPR Mode:.+Will boot as in-chassis active'
        self.proceed_switchover = r'^.*Proceed with switchover to standby RP\? \[confirm\]'
