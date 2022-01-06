
from unicon.core.errors import StateMachineError
from unicon.plugins.iosxe.statemachine import IosXESingleRpStateMachine, boot_from_rommon
from unicon.plugins.generic.statements import GenericStatements, buffer_wait
from unicon.statemachine import State, Path
from unicon.eal.dialogs import Dialog, Statement

from ..statements import boot_from_rommon_statement_list

from .patterns import IosXECat9kPatterns
from .statements import (
    reload_to_rommon_statement_list)


patterns = IosXECat9kPatterns()
statements = GenericStatements()


def container_to_enable_transition(statemachine, spawn, context):
    ''' Exit from container back to enable mode
    '''
    commands = spawn.settings.CONTAINER_EXIT_CMDS

    dialog = Dialog([Statement(pattern=statemachine.get_state('container_shell').pattern,
                               loop_continue=False,
                               trim_buffer=True),
                     Statement(pattern=statemachine.get_state('enable').pattern,
                               loop_continue=False,
                               trim_buffer=False),
                     statements.syslog_msg_stmt
                     ])

    for cmd in commands:
        spawn.send(cmd)
        dialog.process(spawn, context=context)
        statemachine.detect_state(spawn)
        if statemachine.current_state == 'enable':
            return
    else:
        raise StateMachineError('Unable to transition from container shell to enable mode')


class IosXECat9kSingleRpStateMachine(IosXESingleRpStateMachine):
    def create(self):
        super().create()

        container_shell = State('container_shell', patterns.container_shell_prompt)
        container_ssh = State('container_ssh', patterns.container_ssh_prompt)

        rommon = self.get_state('rommon')
        disable = self.get_state('disable')
        enable = self.get_state('enable')

        self.add_state(container_shell)
        self.add_state(container_ssh)

        rommon.pattern = patterns.rommon_prompt

        self.remove_path('rommon', 'disable')
        self.remove_path('enable', 'rommon')

        rommon_to_disable = Path(rommon, disable, boot_from_rommon, Dialog(
            boot_from_rommon_statement_list))
        enable_to_rommon = Path(enable, rommon, 'reload', Dialog(
            reload_to_rommon_statement_list))

        container_shell_to_enable = Path(container_shell, enable, container_to_enable_transition, None)

        self.add_path(rommon_to_disable)
        self.add_path(enable_to_rommon)
        self.add_path(container_shell_to_enable)
