from datetime import datetime
from unicon.eal.dialogs import Dialog, Statement
from unicon.plugins.generic.statements import default_statement_list, generic_statements
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine, config_transition
from unicon.plugins.nxos.patterns import NxosPatterns
from unicon.statemachine import State, Path

from .statements import boot_image, boot_prompt_stmt, boot_statement_list

patterns = NxosPatterns()


def boot_from_rommon(statemachine, spawn, context):
    context['boot_start_time'] = datetime.now()
    context['boot_prompt_count'] = 1
    boot_image(spawn, context, None)
    dialog = Dialog([
        boot_prompt_stmt,
        Statement(
            pattern=patterns.enable_prompt,
            loop_continue = False,
            trim_buffer=False
        )] + boot_statement_list)
    dialog.process(spawn=spawn, context=context)


def boot_from_boot(statemachine, spawn, context):
    context['boot_start_time'] = datetime.now()
    spawn.sendline('load-nxos')


def attach_module(state_machine, spawn, context):
    spawn.sendline('attach module %s' % context.get('_module_num', '1'))


def send_config_cmd(state_machine, spawn, context):
    state_machine.config_command = 'config dual-stage' if context.get('config_dual') else 'config term'
    config_transition(state_machine, spawn, context)


def shell_to_l2rib_dt_transition(state_machine, spawn, context):
    spawn.sendline('/isan/bin/l2rib_dt %s' % context.get('_client_id', '-r'))


class NxosSingleRpStateMachine(GenericSingleRpStateMachine):

    def create(self):
        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)
        shell = State('shell', patterns.shell_prompt)
        loader = State('rommon', patterns.loader_prompt)
        guestshell = State('guestshell', patterns.guestshell_prompt)
        module = State('module', patterns.module_prompt)
        module_elam = State('module_elam', patterns.module_elam_prompt)
        module_elam_insel = State('module_elam_insel', patterns.module_elam_insel_prompt)
        debug = State('debug', patterns.debug_prompt)
        sqlite = State('sqlite', patterns.sqlite_prompt)
        l2rib_dt = State('l2rib_dt', patterns.l2rib_dt_prompt)
        boot = State('boot', patterns.boot_prompt)
        boot_config = State('boot_config', patterns.boot_config_prompt)

        loader_to_enable = Path(loader, enable, boot_from_rommon, Dialog(
            boot_statement_list))

        enable_to_config = Path(enable, config, send_config_cmd, None)
        config_to_enable = Path(config, enable, 'end', Dialog([
            Statement(pattern=patterns.commit_changes_prompt,
                      action='sendline(no)',
                      loop_continue=True)
        ]))

        enable_to_shell = Path(enable, shell, 'run bash', None)
        shell_to_enable = Path(shell, enable, 'exit', None)

        enable_to_guestshell = Path(enable, guestshell, 'guestshell', None)
        guestshell_to_enable = Path(guestshell, enable, 'exit', None)

        enable_to_module = Path(enable, module, attach_module, Dialog([generic_statements.login_stmt]))
        module_to_enable = Path(module, enable, 'exit', None)
        module_elam_to_module = Path(module_elam, module, 'exit', None)
        module_elam_insel_to_module = Path(module_elam_insel, module_elam, 'exit', None)

        debug_to_enable = Path(debug, enable, 'exit', None)
        sqlite_to_debug = Path(sqlite, debug, '.exit', None)

        shell_to_l2rib_dt = Path(shell, l2rib_dt, shell_to_l2rib_dt_transition, None)
        l2rib_dt_to_shell = Path(l2rib_dt, shell, 'exit', None)

        boot_to_boot_config = Path(boot, boot_config, 'config terminal', None)
        boot_config_to_boot = Path(boot_config, boot, 'end', None)

        boot_to_enable = Path(boot, enable, boot_from_boot, Dialog(boot_statement_list))

        boot_to_shell = Path(boot, shell, 'start', None)
        shell_to_boot = Path(shell, boot, 'exit', None)


        # Add State and Path to State Machine
        self.add_state(enable)
        self.add_state(config)
        self.add_state(shell)
        self.add_state(loader)
        self.add_state(guestshell)
        self.add_state(module)
        self.add_state(module_elam)
        self.add_state(module_elam_insel)
        self.add_state(debug)
        self.add_state(sqlite)
        self.add_state(l2rib_dt)
        self.add_state(boot)
        self.add_state(boot_config)


        self.add_path(loader_to_enable)
        self.add_path(enable_to_config)
        self.add_path(config_to_enable)
        self.add_path(enable_to_shell)
        self.add_path(shell_to_enable)
        self.add_path(enable_to_guestshell)
        self.add_path(guestshell_to_enable)
        self.add_path(enable_to_module)
        self.add_path(module_to_enable)
        self.add_path(module_elam_to_module)
        self.add_path(module_elam_insel_to_module)
        self.add_path(debug_to_enable)
        self.add_path(sqlite_to_debug)
        self.add_path(shell_to_l2rib_dt)
        self.add_path(l2rib_dt_to_shell)
        self.add_path(boot_to_boot_config)
        self.add_path(boot_config_to_boot)
        self.add_path(boot_to_enable)
        self.add_path(boot_to_shell)
        self.add_path(shell_to_boot)


        self.add_default_statements(default_statement_list)


class NxosDualRpStateMachine(NxosSingleRpStateMachine):
    def create(self):
        super().create()
