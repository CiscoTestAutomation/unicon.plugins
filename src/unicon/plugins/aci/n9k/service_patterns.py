__author__ = "dwapstra"

from unicon.plugins.generic.service_patterns import ReloadPatterns

class AciN9kReloadPatterns(ReloadPatterns):
    def __init__(self):
        super().__init__()
        self.restart_proceed = r'^(.*?)This command will reload the chassis, Proceed \(y/n\)\? \[n\]:'
        self.factory_reset = r'^(.*?)This command will wipe out this device, Proceed\? \[y/N\]'
        self.login = r'^(.*?)login:'
        self.discovery_done = r'^(.*)This switch is now part of the ACI fabric'
