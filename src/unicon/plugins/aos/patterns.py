'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''
from unicon.plugins.generic.patterns import GenericPatterns


class aosPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.login_prompt = r' *login as: *?'
        self.disable_mode = r'\w+#'
        self.privileged_mode = r'\w+.config.#'
        self.config_mode = r'\w+.config.#'
        self.password = r'Password:'
