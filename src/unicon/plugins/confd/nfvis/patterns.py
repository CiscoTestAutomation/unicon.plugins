""" NFVIS regex patterns """

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


from ..patterns import ConfdPatterns

class NfvisPatterns(ConfdPatterns):
    def __init__(self):
        super().__init__()
        self.cisco_prompt = r'^(.*?)(%N|nfvis)#\s*$'
        self.cisco_config_prompt = r'^(.*?)((%N|nfvis)\(config.*\)#)\s*$'
        self.cisco_commit_changes_prompt = r'Uncommitted changes found, commit them\? \[yes/no/CANCEL\]'
