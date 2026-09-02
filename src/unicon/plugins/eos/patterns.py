'''
Author: Richard Day
Contact: https://www.linkedin.com/in/richardday/, https://github.com/rich-day

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

import re
from unicon.plugins.generic.patterns import GenericPatterns


class EOSPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.login_prompt = r'^ *login: *?'
        self.disable_mode = r'^(.*?)\w+>$'
        self.privileged_mode = r'^(.*?)\w+[^\(config\)]#$'
        self.password = r'Password:'