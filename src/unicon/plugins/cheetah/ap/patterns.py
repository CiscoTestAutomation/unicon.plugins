""" Generic Cheetah AP Patterns. """

__author__ = "Naveen <navevenu@cisco.com>"

from unicon.plugins.generic.patterns import GenericPatterns


class CheetahAPPatterns(GenericPatterns):

    def __init__(self):
        super().__init__()
        self.ap_shell_prompt = r'^(.*?)\w+:\/(.*?)#\s?$'