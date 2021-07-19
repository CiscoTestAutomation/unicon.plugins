__author__ = "dwapstra"

from ..patterns import NxosPatterns


class AciPatterns(NxosPatterns):
    def __init__(self):
        super().__init__()
        self.enable_prompt = r'^(.*?)((%N)|\(none\))#'
        self.loader_prompt = r'^(.*?)loader >\s*$'
