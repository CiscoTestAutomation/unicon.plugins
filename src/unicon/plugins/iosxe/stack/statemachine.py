""" Stack IOS-XE state machine """
from unicon.plugins.iosxe.statemachine import IosXESingleRpStateMachine
from unicon.plugins.generic.statements import connection_statement_list
from unicon.plugins.generic.service_statements import reload_statement_list
from .patterns import StackIosXEPatterns
from unicon.statemachine import State, Path
from unicon.eal.dialogs import Dialog
from .service_statements import boot_from_rommon

patterns = StackIosXEPatterns()


class StackIosXEStateMachine(IosXESingleRpStateMachine):
    def create(self):
        super().create()

        self.remove_path('enable', 'rommon')
        self.remove_path('rommon', 'disable')
        self.remove_state('rommon')

        rommon = State('rommon', patterns.rommon_prompt)
        enable_to_rommon = Path(self.get_state('enable'), rommon, 'reload',
            Dialog(reload_statement_list))
        rommon_to_disable = Path(rommon, self.get_state('disable'), boot_from_rommon,
            Dialog(connection_statement_list))
        self.add_state(rommon)
        self.add_path(enable_to_rommon)
        self.add_path(rommon_to_disable)
