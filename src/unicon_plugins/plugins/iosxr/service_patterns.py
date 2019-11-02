

class IOSXRSwitchoverPatterns:
    def __init__(self):
        self.prompt_switchover = r'^(.*?)Proceed with switchover .* \[confirm\]'
        self.rp_in_standby = r'^(.*?) is in standby'

