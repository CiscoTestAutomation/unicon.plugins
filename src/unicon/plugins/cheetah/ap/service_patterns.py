"""Cheetah AP service patterns."""

from unicon.plugins.generic.service_patterns import (
    PingPatterns as GenericPingPatterns,
    ReloadPatterns,
)


class APReloadPatterns(ReloadPatterns):
    def __init__(self):
        super().__init__()
        self.ap_shell_prompt = r'^Proceed with reload (command (\W+cold\W)?)?(\?) (\[)+confirm+(\])$'


class PingPatterns(GenericPingPatterns):
    """Cheetah AP ping patterns."""

    def __init__(self):
        super().__init__()
        # Data pattern [0xABCD]: 0x
        self.data_pattern = r'(?:^|\r\n)Data pattern \[[^\]\r\n]+\]: 0x$'
        # Sweep range of sizes [n]:
        self.range = r'^Sweep range of sizes \[n\]:\s*$'
