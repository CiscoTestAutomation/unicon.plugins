"""Regex patterns relevant to the iosxe/ewc Unicon plugin

Copyright (c) 2019-2020 by cisco Systems, Inc.
All rights reserved.
"""

from unicon.plugins.iosxe.patterns import IosXEPatterns


class IosXEEWCGenericPatterns(IosXEPatterns):
    def __init__(self):
        super().__init__()
        self.iosxe_glean_pattern = r'Cisco IOS XE Software'
        self.ap_glean_pattern = r'Cisco AP Software'

        self.ap_disable_prompt = r'^(.*?)(?P<hostname0>\S+)>\s*$'
        self.ap_enable_prompt = r'^(.*?)(?P<hostname0>[\w\.\d]+)(?!\(conf.*?\))?#\s*$'


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Bash Shell Patterns
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
class IosXEEWCBashShellPatterns(IosXEEWCGenericPatterns):
    def __init__(self):
        super().__init__()
        self.coral_hostname = 'Coral-mewlc'
        self.coral_are_you_sure = r'^Are you sure you want to continue\?\s+\[y\/n\]\s+$'
        self.coral_hostname_enable = r'^{}#\s?$'.format(self.coral_hostname)


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# AP Shell Patterns
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
class IosXEEWCAPShellPatterns(IosXEEWCGenericPatterns):
    def __init__(self):
        super().__init__()
        self.ap_are_you_sure = r'^.*Are you sure you want to continue connecting.*$'
        self.ap_password = r'^.* password:\s?$'
        self.ap_enable = r'^Password:\s?$'
