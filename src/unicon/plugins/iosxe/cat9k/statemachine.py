from datetime import datetime

from ..service_statements import boot_image
from unicon.plugins.iosxe.statemachine import IosXESingleRpStateMachine
from unicon.statemachine import State, Path
from unicon.eal.dialogs import Dialog

from .patterns import IosXECat9kPatterns
from .statements import (
    rommon_boot_statement_list,
    reload_to_rommon_statement_list,
    boot_timeout_stmt)


patterns = IosXECat9kPatterns()


def boot_from_rommon(statemachine, spawn, context):
    context['boot_start_time'] = datetime.now()
    boot_image(spawn, context, None)


class IosXECat9kSingleRpStateMachine(IosXESingleRpStateMachine):
    def create(self):
        super().create()

        container_shell = State('container_shell', patterns.container_shell_prompt)

        rommon = self.get_state('rommon')
        disable = self.get_state('disable')
        enable = self.get_state('enable')

        self.add_state(container_shell)

        rommon.pattern = patterns.rommon_prompt

        self.remove_path('rommon', 'disable')
        self.remove_path('enable', 'rommon')

        rommon_to_disable = Path(rommon, disable, boot_from_rommon, Dialog(
            rommon_boot_statement_list + [boot_timeout_stmt]))
        enable_to_rommon = Path(enable, rommon, 'reload', Dialog(
            reload_to_rommon_statement_list))

        container_shell_to_enable = Path(container_shell, enable, 'exit', None)

        self.add_path(rommon_to_disable)
        self.add_path(enable_to_rommon)
        self.add_path(container_shell_to_enable)
