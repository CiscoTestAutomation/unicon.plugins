__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.plugins.nxos.service_patterns \
    import ReloadPatterns as BaseNxosReloadPatterns

class NxosN5kReloadPatterns(BaseNxosReloadPatterns):
    def __init__(self):
        super().__init__()
        self.reload_confirm_nxos = r'.*This command will reboot the system[\n\r]*Do you want to continue\?\s*\(y/n\)\s*\[n\]\s*$'
