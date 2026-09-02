from time import sleep
from unicon.statemachine import State, Path
from unicon.core.errors import StateMachineError, TimeoutError as UniconTimeoutError
from unicon.eal.dialogs import Dialog, Statement
from unicon.plugins.generic.statements import GenericStatements, update_context, chatty_term_wait, syslog_wait_send_return

from ..statemachine import FxosStateMachine
from ..patterns import FxosPatterns
from ..statements import fxos_statements

patterns = FxosPatterns()
generic_statements = GenericStatements()

enable_dialog = Dialog([
    fxos_statements.enable_username_stmt,
    fxos_statements.enable_password_stmt,
    generic_statements.syslog_msg_stmt
])


def connect_module(state_machine, spawn, context):
    """ Module state change handler

    When connecting to the module, the connection can end up in different states.
    This state change handler is detecting the state and perfoming additional state
    transitions as needed by calling the go_to statemachine service.
    """
    sm = state_machine

    spawn.sendline('connect module {} {}'.format(context.get('_module', 1), context.get('_mod_con_type', 'console')))
    sm.go_to('any',
             spawn,
             timeout=spawn.timeout,
             context=context,
             dialog=Dialog([generic_statements.escape_char_stmt]) + enable_dialog)

    if sm.current_state != 'module':
        sm.go_to('module', spawn, context=context, hop_wise=True, timeout=spawn.timeout)

    # send newline so the state transition can pick up the new state
    spawn.sendline()


def module_to_fxos_transition(statemachine, spawn, context):
    if context.get('_mod_con_type') == 'telnet':
        spawn.sendline('exit')
        dialog = Dialog([
            Statement(pattern=patterns.no_such_command,
                      action='send(~)',
                      args=None,
                      loop_continue=True),
            Statement(pattern=patterns.telnet_escape_prompt,
                      action='sendline(q)', args=None,
                      loop_continue=False),
        ])
        statemachine.go_to('any', spawn, timeout=spawn.timeout, dialog=dialog)
        spawn.sendline()
    else:
        try:
            spawn.send('~\x17')   # ~ should be sufficient, but tests show ctrl-w is needed
            spawn.expect(patterns.telnet_escape_prompt,
                         timeout=10,
                         log_timeout=False)
            spawn.sendline('q')
        except UniconTimeoutError:
            spawn.sendline('\x17')   # Ctrl-W to clear the line
            chatty_term_wait(spawn)
            spawn.sendline('exit')


def ftd_to_module_transition(statemachine, spawn, context):
    if context.get('console'):
        spawn.sendline('exit')
    else:
        raise StateMachineError('Not on console, cannot transition')


def connect_adapter(state_machine, spawn, context):
    spawn.sendline('connect adapter %s' % context.get('_adapter_module', '1/1/1'))


def connect_cimc(state_machine, spawn, context):
    spawn.sendline('connect cimc %s' % context.get('_cimc_module', '1/1'))


def module_to_asa_transition(statemachine, spawn, context, to_state):
    # If the module is not running ASA, connect to FTD first
    # This is known if we have tried to connect before
    if context.get('_module_{}_asa'.format(
            context.get('_module', 1))) is False:
        spawn.sendline('connect ftd')
        statemachine.go_to('ftd',
                           spawn,
                           timeout=spawn.timeout,
                           context=context)
        spawn.sendline('system support diagnostic-cli')
    else:
        spawn.sendline('connect asa')
        chatty_term_wait(spawn)

    # Check if we ended up on the ASA or stayed on the module
    # Set flag so next time we go via FTD directly
    dialog = Dialog([
        Statement(pattern=patterns.asa_is_not_running,
                    action=update_context,
                    args={'_module_{}_asa'.format(
                        context.get('_module', 1)): False},
                    loop_continue=True)
    ]) + enable_dialog
    statemachine.go_to(['disable', 'enable', 'config', 'module'],
                       spawn,
                       timeout=spawn.timeout,
                       context=context,
                       dialog=dialog)

    # If we stayed on the module, probably ASA is not running
    # Connect via FTD
    if statemachine.current_state == 'module':
        spawn.sendline('connect ftd')
        statemachine.go_to('ftd',
                           spawn,
                           timeout=spawn.timeout,
                           context=context,
                           dialog=enable_dialog)
        spawn.sendline('system support diagnostic-cli')
        statemachine.go_to(['disable', 'enable', 'config'],
                           spawn,
                           timeout=spawn.timeout,
                           context=context,
                           dialog=enable_dialog)

    # If we did not end up in the target state, go there now
    if statemachine.current_state != to_state:
        statemachine.go_to(to_state,
                           spawn,
                           timeout=spawn.timeout,
                           context=context,
                           dialog=enable_dialog)

    spawn.sendline()


def raise_ftd_not_running():
    raise StateMachineError('FTD is not running')


def module_to_asa_disable_transition(statemachine, spawn, context):
    module_to_asa_transition(statemachine, spawn, context, 'disable')


def module_to_asa_config_transition(statemachine, spawn, context):
    module_to_asa_transition(statemachine, spawn, context, 'config')


def module_to_asa_enable_transition(statemachine, spawn, context):
    module_to_asa_transition(statemachine, spawn, context, 'enable')


def asa_to_ftd_transition(statemachine, spawn, context):
    spawn.read_update_buffer()
    spawn.send('\x01d')  # Ctrl-A D
    statemachine.go_to(['ftd', 'module'],
                       spawn,
                       timeout=spawn.timeout,
                       context=context)
    if statemachine.current_state == 'module':
        spawn.sendline('connect ftd')
        dialog = Dialog([
            Statement(pattern=patterns.ftd_is_not_running,
                        action=raise_ftd_not_running,
                        args=None)
        ])
        statemachine.go_to(['disable', 'enable', 'config', 'module'],
                           spawn,
                           timeout=spawn.timeout,
                           dialog=dialog)
    else:
        spawn.sendline()


def asa_to_module_transition(statemachine, spawn, context):
    spawn.read_update_buffer()
    spawn.send('\x01d')  # Ctrl-A D
    statemachine.go_to(['ftd', 'module'], spawn, timeout=spawn.timeout, context=context)
    if statemachine.current_state == 'ftd':
        ftd_to_module_transition(statemachine, spawn, context)
    else:
        spawn.sendline()


class FxosFp4kStateMachine(FxosStateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        super().create()

        enable = self.get_state('enable')
        disable = self.get_state('disable')
        config = self.get_state('config')
        ftd = self.get_state('ftd')
        fxos = self.get_state('fxos')
        rommon = self.get_state('rommon')

        self.remove_path(ftd, fxos)
        self.remove_path(fxos, ftd)

        self.remove_path(ftd, rommon)

        self.remove_path(enable, ftd)
        self.remove_path(disable, ftd)
        self.remove_path(config, ftd)

        adapter = State('adapter', patterns.adapter_prompt)
        adapter_shell = State('adapter_shell', patterns.adapter_shell_prompt)
        adapter_shell_fls = State('adapter_shell_fls', patterns.adapter_shell_fls)
        adapter_shell_mcp = State('adapter_shell_mcp', patterns.adapter_shell_mcp)
        cimc = State('cimc', patterns.cimc_prompt)
        fxos_switch = State('fxos_switch', patterns.fxos_switch_prompt)
        module = State('module', patterns.module_prompt)

        fxos_to_adapter = Path(fxos, adapter, connect_adapter, None)
        adapter_to_adapter_shell = Path(adapter, adapter_shell, 'connect', None)
        adapter_shell_to_adapter = Path(adapter_shell, adapter, 'exit', None)
        adapter_shell_to_adapter_shell_fls = Path(adapter_shell, adapter_shell_fls, 'attach-fls', None)
        adapter_shell_fls_to_adapter_shell = Path(adapter_shell_fls, adapter_shell, 'exit', None)
        adapter_shell_to_adapter_shell_mcp = Path(adapter_shell, adapter_shell_mcp, 'attach-mcp', None)
        adapter_shell_mcp_to_adapter_shell = Path(adapter_shell_mcp, adapter_shell, 'exit', None)

        adapter_to_fxos = Path(adapter, fxos, 'exit', None)
        fxos_to_cimc = Path(fxos, cimc, connect_cimc, None)
        cimc_to_fxos = Path(cimc, fxos, 'exit', None)
        fxos_to_fxos_switch = Path(fxos, fxos_switch, 'connect fxos', None)
        fxos_switch_to_fxos = Path(fxos_switch, fxos, 'exit', None)

        fxos_to_module = Path(fxos, module, connect_module, None)
        module_to_fxos = Path(module, fxos, module_to_fxos_transition, None)

        module_to_ftd = Path(module, ftd, 'connect ftd', Dialog([
            Statement(patterns.ftd_console_exit,
                      action=update_context,
                      args={'console': True},
                      loop_continue=True),
            Statement(pattern=patterns.ftd_is_not_running,
                      action=raise_ftd_not_running,
                      args=None)
        ]))
        ftd_to_module = Path(ftd, module, ftd_to_module_transition, None)

        module_to_disable = Path(module, disable, module_to_asa_disable_transition, None)
        disable_to_module = Path(disable, module, asa_to_module_transition, None)
        module_to_enable = Path(module, enable, module_to_asa_enable_transition, None)
        enable_to_module = Path(enable, module, asa_to_module_transition, None)
        module_to_config = Path(module, config, module_to_asa_config_transition, None)
        config_to_module = Path(config, module, asa_to_module_transition, None)

        disable_to_ftd = Path(disable, ftd, asa_to_ftd_transition, None)
        enable_to_ftd = Path(enable, ftd, asa_to_ftd_transition, None)
        config_to_ftd = Path(config, ftd, asa_to_ftd_transition, None)

        self.add_state(adapter)
        self.add_state(cimc)
        self.add_state(fxos_switch)
        self.add_state(module)
        self.add_state(adapter_shell)
        self.add_state(adapter_shell_fls)
        self.add_state(adapter_shell_mcp)

        self.add_path(fxos_to_adapter)
        self.add_path(adapter_to_fxos)
        self.add_path(adapter_to_adapter_shell)
        self.add_path(adapter_shell_to_adapter)
        self.add_path(adapter_shell_to_adapter_shell_fls)
        self.add_path(adapter_shell_fls_to_adapter_shell)
        self.add_path(adapter_shell_to_adapter_shell_mcp)
        self.add_path(adapter_shell_mcp_to_adapter_shell)

        self.add_path(fxos_to_cimc)
        self.add_path(cimc_to_fxos)
        self.add_path(fxos_to_module)
        self.add_path(module_to_fxos)
        self.add_path(fxos_to_fxos_switch)
        self.add_path(fxos_switch_to_fxos)
        self.add_path(module_to_ftd)
        self.add_path(ftd_to_module)

        self.add_path(module_to_disable)
        self.add_path(disable_to_module)
        self.add_path(module_to_enable)
        self.add_path(enable_to_module)
        self.add_path(module_to_config)
        self.add_path(config_to_module)

        self.add_path(disable_to_ftd)
        self.add_path(enable_to_ftd)
        self.add_path(config_to_ftd)
