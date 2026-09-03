__author__ = "Takashi Higashimura <tahigash@cisco.com>"

from unicon.plugins.iosxr.service_patterns import IOSXRReloadPatterns

class IOSXRASR9KReloadPatterns(IOSXRReloadPatterns):
    def __init__(self):
        super().__init__()
        self.system_config_completed = r"^(.*?)SYSTEM CONFIGURATION COMPLETED"
        self.reloading_node = r"^(.*?)Reloading node .*"
