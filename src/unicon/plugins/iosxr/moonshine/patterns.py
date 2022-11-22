
from unicon.plugins.iosxr.patterns import IOSXRPatterns

# This module contains all the patterns required in the Moonshine implementation.

class MoonshinePatterns(IOSXRPatterns):
    def __init__(self):
        super().__init__()
        self.shell_prompt = r'^(.*)%N.[0-9][1-9]*/[0-9][1-9]*/CPU[0-9][1-9]*\.*[0|1]*(\x1b\S+)?/*\s?[#\$].*$'
        self.enable_prompt = r'^(.*)RP/[0-9][1-9]*/[0-9][1-9]*/CPU[0-9][1-9]*:[a-zA-Z0-9_.{}+-]+#.*$'
        self.config_prompt = r'^(.*)RP/[0-9][1-9]*/[0-9][1-9]*/CPU[0-9][1-9]*:[a-zA-Z0-9_.{}+-]+\(config.*\)#.*$'
