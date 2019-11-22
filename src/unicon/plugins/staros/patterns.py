__author__ = "dwapstra"

from unicon.plugins.generic.patterns import GenericPatterns

class StarosPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.exec_prompt = r'^(.*?)(\[\S+\]%N[#>])\s*$'
        self.config_prompt = r'^(.*?)(\[\S+\]%N\(\S+\)[#>])\s*$'

        self.yes_no_prompt = r'^(.*?)Are you sure \? \[Yes | No\]:\s*'

