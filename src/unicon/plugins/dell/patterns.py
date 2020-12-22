'''
Author: Knox Hutchinson
Contact: https://dataknox.dev
https://twitter.com/data_knox
https://youtube.com/c/dataknox
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''
import re

from unicon.plugins.generic.patterns import GenericPatterns


class DellPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.login_prompt = r' *login here: *?'
        self.disable_mode = r'\w+>$'
        self.privileged_mode = r'\w+[^\(config\)]#$'
        self.config_mode = r'\w+\(config[-\w]+\)#$'
        self.password = r'Password:'
