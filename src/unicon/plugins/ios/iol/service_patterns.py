__author__ = 'Difu Hu <difhu@cisco.com>'

from unicon.plugins.generic.service_patterns import HaReloadPatterns


class IosIolHaReloadPatterns(HaReloadPatterns):
    def __init__(self):
        super().__init__()
        self.reload_switch_prompt = \
            r'^.*This will reload the active unit and force a switch of activity \[confirm\]\s*$'
