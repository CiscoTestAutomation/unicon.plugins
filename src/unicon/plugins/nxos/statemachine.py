from unicon.eal.dialogs import Dialog, Statement
from unicon.plugins.generic.statements import default_statement_list
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine, config_transition
from unicon.plugins.nxos.patterns import NxosPatterns
from unicon.statemachine import State, Path


patterns = NxosPatterns()


def attach_module(state_machine, spawn, context):
    spawn.sendline('attach module %s' % context.get('_module_num', '1'))


def send_config_cmd(state_machine, spawn, context):
    state_machine.config_command = 'config dual-stage' if context.get('config_dual') else 'config term'
    config_transition(state_machine, spawn, context)


class NxosSingleRpStateMachine(GenericSingleRpStateMachine):

    def create(self):
        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)
        shell = State('shell', patterns.shell_prompt)
        loader = State('loader', patterns.loader_prompt)
        guestshell = State('guestshell', patterns.guestshell_prompt)
        module = State('module', patterns.module_prompt)
        module_elam = State('module_elam', patterns.module_elam_prompt)
        module_elam_insel = State('module_elam_insel', patterns.module_elam_insel_prompt)
        debug = State('debug', patterns.debug_prompt)
        sqlite = State('sqlite', patterns.sqlite_prompt)

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

        enable_to_module = Path(enable, module, attach_module, None)
        module_to_enable = Path(module, enable, 'exit', None)
        module_elam_to_module = Path(module_elam, module, 'exit', None)
        module_elam_insel_to_module = Path(module_elam_insel, module_elam, 'exit', None)

        debug_to_enable = Path(debug, enable, 'exit', None)
        sqlite_to_debug = Path(sqlite, debug, '.exit', None)

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

        self.add_default_statements(default_statement_list)


class NxosDualRpStateMachine(NxosSingleRpStateMachine):
    def create(self):
        super().create()
