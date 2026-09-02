__author__ = "Takashi Higashimura <tahigash@cisco.com>"

from unicon.plugins.generic.service_patterns import ReloadPatterns


class IOSXRSwitchoverPatterns:
    def __init__(self):
        self.prompt_switchover = r'^(.*?)Proceed with switchover .* \[confirm\]'
        self.rp_in_standby = r'^(.*?) is in standby'
        self.switchover_disallowed = r'^(.*?)Switchover disallowed'


class IOSXRReloadPatterns(ReloadPatterns):
    def __init__(self):
        super().__init__()
        self.reload_module_prompt = r"^(.*?)Reload hardware module \? \[no,yes\].*$"
        self.wish_continue = r'Do you wish to continue\?\s*\[confirm\(y/n\)\]\s*$'
