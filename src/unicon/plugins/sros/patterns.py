__author__ = 'Difu Hu <pyats-support@cisco.com;pyats-support-ext@cisco.com>'

from unicon.patterns import UniconCorePatterns


class SrosPatterns(UniconCorePatterns):

    def __init__(self):
        super().__init__()
        self.continue_connect = r'Are you sure you want to continue connecting \(yes/no(/\[fingerprint\])?\)'
        self.permission_denied = r'^Permission denied, please try again\.\s?$'
        self.mdcli_prompt = r'^(.*?)\[.*\][\r\n]+[AB]:.*@%N#\s?$'
        self.classiccli_prompt = r'^(.*?)\*?[AB]:%N(>.*)?#\s?$'
        self.discard_uncommitted = r'Discard uncommitted changes\? \[y,n\]'
