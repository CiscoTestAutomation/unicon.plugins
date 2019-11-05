""" NFVIS regex patterns """

__copyright__ = "# Copyright (c) 2018 by cisco Systems, Inc. All rights reserved."
__author__ = "Dave Wapstra <dwapstra@cisco.com>"


from unicon.plugins.confd.patterns import ConfdPatterns

class ViptelaPatterns(ConfdPatterns):
    def __init__(self):
        super().__init__()
        self.cisco_prompt = r'^(.*?)((%N|vedge)#)\s*$'
        self.cisco_config_prompt = r'^(.*?)(%N\(config.*\)#)\s*$'
        self.cisco_commit_changes_prompt = r'Uncommitted changes found, commit them\? \[yes/no/CANCEL\]'
        self.shell_prompt = r'^(.*?%N\s?([-\w\]/~\s:\d]+)?[>\$~%#])\s?$'
