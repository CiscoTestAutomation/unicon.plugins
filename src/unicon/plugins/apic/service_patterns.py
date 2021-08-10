__author__ = "dwapstra"

from unicon.plugins.generic.service_patterns import ReloadPatterns


class ApicReloadPatterns(ReloadPatterns):
    def __init__(self):
        super().__init__()
        self.restart_proceed = r'^(.*?)This command will restart (this device|the APIC), Proceed\? \[y/N\]'
        self.factory_reset = r'^(.*?)Do you want to restore this APIC to factory settings\? The system will be REBOOTED. \(Y/n\):'
        self.press_any_key = r'^(.*?)Press any key to continue'
        self.login = r'^(.*?)login:'
