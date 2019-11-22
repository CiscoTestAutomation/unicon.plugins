__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon.plugins.nxos.patterns import NxosPatterns

class NxosMdsPatterns(NxosPatterns):
    def __init__(self):
        super().__init__()

        self.shell_prompt = r'^(.*)%N\(shell\)>\s?.*$'

