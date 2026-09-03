__author__ = "dwapstra"

from unicon.plugins.fxos.patterns import FxosPatterns


class AsaFp2kPatterns(FxosPatterns):
    def __init__(self):
        super().__init__()
        self.fxos_prompt = r'^(.*?)firepower.*?#\s*$'
        self.broken_pipe = r'.*Connection to .*Broken pipe'
        self.reload_confirm = r'^(.*?)Proceed with reload\? \[confirm\]'
