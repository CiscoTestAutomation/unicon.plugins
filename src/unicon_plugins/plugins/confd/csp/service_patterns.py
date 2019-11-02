
from unicon.patterns import UniconCorePatterns

class ReloadPatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        self.reload_confirm = r'^(.*?)Are you sure you want to reboot the system\? \[no,yes\]\s*$'
