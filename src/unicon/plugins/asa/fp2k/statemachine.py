""" State machine for ASA/FP2K """

__author__ = "dwapstra"

from unicon.statemachine import Path
from unicon.eal.dialogs import Dialog
from unicon.plugins.fxos.statemachine import FxosStateMachine

from .statements import boot_to_rommon_statements
from .patterns import AsaFp2kPatterns


patterns = AsaFp2kPatterns()


def connect_fxos(statemachine, spawn, context):
    mode = context.get('_fxos_connect_mode', '')
    spawn.sendline('connect fxos {}'.format(mode).strip())


def send_ctrl_caret_x(statemachine, spawn, context):
    # Send Ctrl-^X
    spawn.send('\x1ex')


def enable_to_rommon_transition(statemachine, spawn, context):
    dialog = Dialog(boot_to_rommon_statements)
    spawn.sendline('reload')
    dialog.process(spawn, timeout=spawn.settings.BOOT_TIMEOUT, context=context)
    spawn.sendline()


class AsaFp2kStateMachine(FxosStateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        super().create()

        enable = self.get_state('enable')
        disable = self.get_state('disable')
        config = self.get_state('config')
        ftd_expert = self.get_state('expert')
        ftd_expert_root = self.get_state('sudo')
        fxos = self.get_state('fxos')
        fxos_mgmt = self.get_state('fxos_mgmt')
        ftd = self.get_state('ftd')
        rommon = self.get_state('rommon')

        fxos.pattern = patterns.fxos_prompt

        self.remove_path(ftd, ftd_expert)
        self.remove_path(ftd_expert, ftd)
        self.remove_path(ftd_expert, ftd_expert_root)
        self.remove_path(ftd_expert_root, ftd_expert)
        self.remove_path(ftd, fxos)
        self.remove_path(fxos, ftd)
        self.remove_path(ftd, enable)
        self.remove_path(enable, ftd)
        self.remove_path(ftd, disable)
        self.remove_path(ftd, config)
        self.remove_path(disable, ftd)
        self.remove_path(config, ftd)
        self.remove_path(ftd, rommon)
        self.remove_path(fxos_mgmt, rommon)
        self.remove_path(rommon, fxos)

        self.remove_state(ftd)

        enable_to_fxos = Path(enable, fxos, connect_fxos, None)
        fxos_to_enable = Path(fxos, enable, send_ctrl_caret_x, None)
        enable_to_ftd_expert_root = Path(enable, ftd_expert_root, 'connect fxos root', None)
        ftd_expert_root_to_enable = Path(ftd_expert_root, enable, 'exit', None)
        enable_to_rommon = Path(enable, rommon, enable_to_rommon_transition, None)
        rommon_to_disable = Path(rommon, disable, 'boot', None)

        self.add_path(enable_to_fxos)
        self.add_path(fxos_to_enable)
        self.add_path(enable_to_ftd_expert_root)
        self.add_path(ftd_expert_root_to_enable)
        self.add_path(enable_to_rommon)
        self.add_path(rommon_to_disable)
