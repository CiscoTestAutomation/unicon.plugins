__author__ = "dwapstra"

from unicon.plugins.generic.patterns import GenericPatterns

class AciPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.enable_prompt = r'^(.*?)((%N)|\(none\))#'
        self.loader_prompt = r'^(.*?)loader >\s*$'
