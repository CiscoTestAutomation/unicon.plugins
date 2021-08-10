
from unicon.plugins.iosxe.statemachine import IosXESingleRpStateMachine
from unicon.eal.dialogs import Dialog, Statement
from ..patterns import IosXEPatterns

patterns = IosXEPatterns()


class SDWANSingleRpStateMachine(IosXESingleRpStateMachine):
    config_command = 'config-transaction'

    def create(self):
        super().create()
        self.get_path('config', 'enable').dialog += Dialog([
            Statement(pattern=patterns.confirm_uncommited_changes,
                      action='sendline(no)', loop_continue=True)
        ])
