"""AP Reload Service Patterns"""

from unicon.plugins.generic.service_patterns import ReloadPatterns

class APReloadPatterns(ReloadPatterns):
    def __init__(self):
        super().__init__()
        self.ap_shell_prompt = r'^Proceed with reload (command (\W+cold\W)?)?(\?) (\[)+confirm+(\])$'