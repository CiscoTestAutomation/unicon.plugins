
from unicon.patterns import UniconCorePatterns

class ReloadPatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        self.system_ready = r'^(.*?)System Ready'
        self.factory_reset_prompt = r'^(.*?)Are you sure you want to reset to factory defaults\? \[yes,NO\]'
        self.reboot_prompt = r'(.*?)Are you sure you want to reboot\? \[yes,NO\]'
