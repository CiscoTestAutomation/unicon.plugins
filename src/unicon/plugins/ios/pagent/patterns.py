
from unicon.plugins.generic.patterns import GenericPatterns

class IosPagentPatterns(GenericPatterns):

    def __init__(self):
        super().__init__()
        self.emu_prompt = r'^(.*?)([\w-]+)\(\w+:.*?\)#\s*$'
