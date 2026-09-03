__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon.plugins.generic.patterns import GenericPatterns

class CimcPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.prompt = r'^(.*?)\S+\s?(/\w+)*\s?#\s*$'
        self.enter_yes_or_no = r"^(.*?)Enter 'yes' or 'no' to confirm.*->\s*$"
