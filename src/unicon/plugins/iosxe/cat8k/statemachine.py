__author__ = "Lukas McClelland <lumcclel@cisco.com>"

from unicon.statemachine import State, Path
from unicon.eal.dialogs import Dialog, Statement
from unicon.plugins.iosxe.statemachine import (
    IosXESingleRpStateMachine,
    IosXEDualRpStateMachine,
    boot_from_rommon
    )
from ..statements import boot_from_rommon_statement_list

from .service_patterns import ReloadPatterns
from .service_statements import (
    reload_to_rommon_statement_list)

patterns = ReloadPatterns()
class IosXECat8kSingleRpStateMachine(IosXESingleRpStateMachine):
    def create(self):
        super().create()

        rommon = self.get_state('rommon')
        disable = self.get_state('disable')
        enable = self.get_state('enable')

        rommon.pattern = patterns.rommon_prompt

        self.remove_path('rommon', 'disable')
        self.remove_path('enable', 'rommon')

        rommon_to_disable = Path(rommon, disable, boot_from_rommon, Dialog(
            boot_from_rommon_statement_list))
        enable_to_rommon = Path(enable, rommon, 'reload', Dialog(
            reload_to_rommon_statement_list))


        self.add_path(rommon_to_disable)
        self.add_path(enable_to_rommon)


class IosXECat8kDualRpStateMachine(IosXEDualRpStateMachine):

    def create(self):
        super().create()

        rommon = self.get_state('rommon')
        disable = self.get_state('disable')
        enable = self.get_state('enable')

        rommon.pattern = patterns.rommon_prompt

        self.remove_path('rommon', 'disable')
        self.remove_path('enable', 'rommon')

        rommon_to_disable = Path(rommon, disable, boot_from_rommon, Dialog(
            boot_from_rommon_statement_list))
        enable_to_rommon = Path(enable, rommon, 'reload', Dialog(
            reload_to_rommon_statement_list))

        self.add_path(rommon_to_disable)
        self.add_path(enable_to_rommon)
