__author__ = "dwapstra"

from unicon.plugins.generic.patterns import GenericPatterns

class FxosPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.shell_prompt = r'^(.*?([>\$~%]|(/[-\w]+)*\*?[^#]+#))\s?$'
