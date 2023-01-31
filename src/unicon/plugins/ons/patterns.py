
from unicon.plugins.iosxr.patterns import IOSXRPatterns

class OnsPatterns(IOSXRPatterns):

    def __init__(self):
        super().__init__()
        self.tl1_prompt = r'(.*?)^\s*>\s*$'
