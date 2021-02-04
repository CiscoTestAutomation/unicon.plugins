'''
Author: Renato Almeida de Oliveira
Contact: renato.almeida.oliveira@gmail.com
https://twitter.com/ORenato_Almeida
https://www.youtube.com/c/RenatoAlmeidadeOliveira
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''
import re

from unicon.plugins.generic.patterns import GenericPatterns


class HPComwarePatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.login_prompt = r'^ *login as: *$'
        self.user_exec_mode = r'^.*<%N>$'
        self.config_mode = r'^ *\[%N(-.*)?\]$'
        self.password = r'^.* password: $'
        self.save_confirm = r'The current configuration will be written to the device\. Are you sure\? \[Y/N\]:'
        self.file_save = r'^.*\(To leave the existing filename unchanged, press the enter key\):'
        self.overwrite = r'^.* exists, overwrite\? \[Y/N\]:'
