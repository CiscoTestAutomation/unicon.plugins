
from unicon.plugins.iosxe.statemachine import IosXESingleRpStateMachine
from unicon.eal.dialogs import Dialog, Statement

class SDWANSingleRpStateMachine(IosXESingleRpStateMachine):
    config_command = 'config-transaction'

    def create(self):
        super().create()
        self.get_path('config', 'enable').dialog = Dialog([
               Statement(pattern=r'Uncommitted changes found, commit them\? \[yes\/no\/CANCEL\]',
                            action='sendline(no)', loop_continue=True)])
