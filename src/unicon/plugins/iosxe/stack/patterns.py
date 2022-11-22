""" IOS-XE Stack Patterns """
from unicon.plugins.iosxe.patterns import IosXEPatterns


class StackIosXEPatterns(IosXEPatterns):
    def __init__(self):
        super().__init__()
        self.rommon_prompt = r'(.*)switch:\s?$'
        self.tcpdump = ".*listening on lfts.*$"