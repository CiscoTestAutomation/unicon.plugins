'''
Author: Yannick Koehler
Contact: yannick@koehler.name
'''
from unicon.plugins.generic.patterns import GenericPatterns


class ArubaosPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.login_prompt = r'User:'
        self.config_mode = r'\w+\(config[-\w]+\)#\s?$'
        self.enable_prompt = r'^\(.*\)\s\*\[.*\]\s#\s?$'
        self.shell_prompt = r'^\(.*\)\s\*\[.*\]\s#\s?$'
