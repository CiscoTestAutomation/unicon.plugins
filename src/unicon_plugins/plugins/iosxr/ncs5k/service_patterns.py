__author__ = "dwapstra"

from unicon_plugins.plugins.generic.service_patterns import ReloadPatterns

class Ncs5kReloadPatterns(ReloadPatterns):
    def __init__(self):
        super().__init__()
        self.system_config_completed = r"^(.*?)SYSTEM CONFIGURATION COMPLETED"
        self.reloading_node = r"^(.*?)Reloading node .*"
