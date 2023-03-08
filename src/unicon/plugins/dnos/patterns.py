'''
Unicon Plugin Patterns
----------------------

Pattern module in a Unicon plugin allows developers to consolidate all
regex patterns that matches dialogs, statements & the likes into one location.

'''

from unicon.plugin.generic.patterns import GenericPatterns


class DnosPatterns(GenericPatterns):

    """
        Class defines all the patterns required
        for dnos
    """
    def __init__(self):
        super().__init__()
        self.continue_connect = r'Are you sure you want to continue connecting \(yes/no(/\[fingerprint\])?\)\s*$'
        self.permission_denied = r'^(.*?)Permission denied(.*?)$'
        # thishostname# 
        self.operation_prompt = r'^(.*?)[\r\n]%N#\s?$'
        # thishostname(cfg-if-bundle-10)# 
        self.configuration_prompt = r'^(.*?)%N\(cfg[-\w]*\)#\s?$'
        # Warning: Configuration includes uncommitted changes, would you like to commit them before exiting (yes/no/cancel) [cancel]? 
        self.commit_changes_prompt = r'^Warning: Configuration includes uncommitted changes, would you like to commit them before exiting \(yes/no/cancel\) \[cancel\]?\s*$'
