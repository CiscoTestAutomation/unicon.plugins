""" State machine for FXOS """

__author__ = "dwapstra"

import re

from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog, Statement
from unicon.core.errors import StateMachineError
from unicon.utils import AttributeDict

from unicon.plugins.generic.statements import GenericStatements, sudo_password_handler, update_context
from unicon.plugins.generic.patterns import GenericPatterns

from .patterns import FxosPatterns
from .statements import fxos_statements, default_statement_list, boot_wait, boot_to_rommon_statements

patterns = FxosPatterns()
generic_statements = GenericStatements()
generic_patterns = GenericPatterns()


def change_fxos_scope(state_machine, spawn, context):
    scopes = [s for s in context.get('_scope', "").split('/') if s]
    for scope in scopes:
        spawn.sendline("scope %s" % scope)
        spawn.expect(state_machine.get_state('fxos_scope').pattern, trim_buffer=False)


def sudo_failed():
    raise Exception('sudo failed')


def send_ctrl_a_d(state_machine, spawn, context):
    spawn.read_update_buffer()
    ctrl_a_d = '\x01d'
    spawn.send(ctrl_a_d)


def ftd_fxos_transition(statemachine, spawn, context):
    sm = statemachine
    console = context.get('console', False)
    if console:
        spawn.sendline('exit')
    else:
        spawn.sendline('connect fxos')
        spawn.expect('.+', trim_buffer=False)
        sm.go_to(['ftd', 'fxos'], spawn, context=context, timeout=spawn.timeout)
        if sm.current_state == 'ftd':
            spawn.sendline('exit')
            context.update({'console': True})
        else:
            spawn.sendline()


def fxos_ftd_transition(statemachine, spawn, context):
    sm = statemachine
    console = context.get('console', False)
    if console:
        spawn.sendline('connect ftd')
    else:
        dialog = Dialog([
            generic_statements.login_stmt, generic_statements.password_stmt,
            Statement(pattern=patterns.you_came_from_fxos,
                      action=update_context,
                      args={'console': True},
                      loop_continue=True)
        ])
        spawn.sendline('exit')
        # Wait a bit using expect, login prompt could appear
        spawn.expect('.+', trim_buffer=False)
        sm.go_to(['ftd', 'disable', 'fxos'], spawn, context=context, timeout=spawn.timeout, dialog=dialog)
        if sm.current_state == 'fxos':
            spawn.sendline('connect ftd')
            context.update({'console': True})
        else:
            spawn.sendline()


def ftd_to_multi_transition(statemachine, spawn, context):
    spawn.sendline('system support diagnostic-cli')
    spawn.sendline()
    statemachine.go_to(['disable', 'enable', 'config'], spawn, timeout=spawn.timeout)


def ftd_to_disable_transition(statemachine, spawn, context):
    ftd_to_multi_transition(statemachine, spawn, context)
    dialog = Dialog([fxos_statements.enable_password_stmt])
    statemachine.go_to('disable', spawn, timeout=spawn.timeout, context=context, dialog=dialog)
    spawn.sendline()


def ftd_to_enable_transition(statemachine, spawn, context):
    ftd_to_multi_transition(statemachine, spawn, context)
    dialog = Dialog([fxos_statements.enable_password_stmt])
    statemachine.go_to('enable', spawn, timeout=spawn.timeout, context=context, dialog=dialog)
    spawn.sendline()


def ftd_to_config_transition(statemachine, spawn, context):
    ftd_to_multi_transition(statemachine, spawn, context)
    dialog = Dialog([fxos_statements.enable_password_stmt])
    statemachine.go_to('config', spawn, timeout=spawn.timeout, context=context, dialog=dialog)
    spawn.sendline()


def boot_fxos(statemachine, spawn, context):
    spawn.sendline('boot')

    boot_wait(spawn, timeout=spawn.settings.BOOT_TIMEOUT)

    spawn.sendline()
    dialog = Dialog([generic_statements.login_stmt, generic_statements.password_stmt,
                     Statement(patterns.fxos_prompt)])
    dialog.process(spawn, context=context)
    spawn.sendline()


class FxosStateMachine(StateMachine):

    STATE_GLEAN = AttributeDict({
        'fxos': AttributeDict(dict(
            command='show version | inc Version',
            pattern=patterns.fxos_glean_pattern)),
        'enable': AttributeDict(dict(
            command='show version | inc Version',
            pattern=patterns.asa_glean_pattern))
    })

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        ftd = State('ftd', patterns.ftd_prompt)
        ftd_expert = State('expert', patterns.ftd_expert_prompt)
        ftd_expert_root = State('sudo', patterns.ftd_expert_root_prompt)
        fxos = State('fxos', patterns.fxos_prompt)
        fxos_scope = State('fxos_scope', patterns.fxos_scope_prompt)
        fxos_local_mgmt = State('fxos_mgmt', patterns.fxos_local_mgmt_prompt)
        enable = State('enable', patterns.enable_prompt)
        disable = State('disable', patterns.disable_prompt)
        config = State('config', patterns.config_prompt)
        rommon = State('rommon', patterns.rommon_prompt)

        ftd_to_ftd_expert = Path(ftd, ftd_expert, 'expert', None)
        ftd_expert_to_ftd = Path(ftd_expert, ftd, 'exit', None)

        ftd_expert_to_ftd_expert_root = Path(
            ftd_expert, ftd_expert_root, 'sudo su -',
            Dialog([
                Statement(generic_patterns.password, sudo_password_handler, None, True, False),
                Statement(patterns.sudo_incorrect_password_pattern, sudo_failed)
            ]))
        ftd_expert_root_to_ftd_expert = Path(ftd_expert_root, ftd_expert, 'exit', None)

        enable_to_disable = Path(enable, disable, 'disable', None)
        enable_to_config = Path(enable, config, 'config term', Dialog([fxos_statements.config_call_home_stmt]))

        disable_to_enable = Path(disable, enable, 'enable', Dialog([
            fxos_statements.enable_username_stmt,
            fxos_statements.enable_password_stmt
        ]))

        config_to_enable = Path(config, enable, 'end', None)

        ftd_to_fxos = Path(ftd, fxos, ftd_fxos_transition, None)
        fxos_to_ftd = Path(fxos, ftd, fxos_ftd_transition, None)
        fxos_scope_to_fxos = Path(fxos_scope, fxos, 'top', None)
        fxos_to_fxos_scope = Path(fxos, fxos_scope, change_fxos_scope, None)

        ftd_to_disable = Path(ftd, disable, ftd_to_disable_transition, Dialog([fxos_statements.enable_password_stmt]))

        ftd_to_enable = Path(ftd, enable, ftd_to_enable_transition, Dialog([fxos_statements.enable_password_stmt]))

        ftd_to_config = Path(ftd, config, ftd_to_config_transition, Dialog([fxos_statements.enable_password_stmt]))

        disable_to_ftd = Path(disable, ftd, send_ctrl_a_d, None)
        enable_to_ftd = Path(enable, ftd, send_ctrl_a_d, None)
        config_to_ftd = Path(config, ftd, send_ctrl_a_d, None)

        fxos_to_local_mgmt = Path(fxos, fxos_local_mgmt, 'connect local-mgmt', None)
        local_mgmt_to_fxos = Path(fxos_local_mgmt, fxos, 'exit', None)

        local_mgmt_to_rommon = Path(fxos_local_mgmt, rommon, 'reboot', Dialog(boot_to_rommon_statements))
        ftd_to_rommon = Path(ftd, rommon, 'reboot', Dialog(boot_to_rommon_statements))

        rommon_to_fxos = Path(rommon, fxos, boot_fxos, None)

        self.add_state(enable)
        self.add_state(disable)
        self.add_state(config)
        self.add_state(ftd)
        self.add_state(ftd_expert)
        self.add_state(ftd_expert_root)
        self.add_state(fxos)
        self.add_state(fxos_scope)
        self.add_state(fxos_local_mgmt)
        self.add_state(rommon)

        self.add_path(enable_to_disable)
        self.add_path(enable_to_config)
        self.add_path(config_to_enable)
        self.add_path(disable_to_enable)
        self.add_path(ftd_to_ftd_expert)
        self.add_path(ftd_expert_to_ftd)
        self.add_path(ftd_expert_to_ftd_expert_root)
        self.add_path(ftd_expert_root_to_ftd_expert)
        self.add_path(ftd_to_fxos)
        self.add_path(fxos_to_ftd)
        self.add_path(fxos_to_fxos_scope)
        self.add_path(fxos_scope_to_fxos)
        self.add_path(ftd_to_enable)
        self.add_path(enable_to_ftd)
        self.add_path(ftd_to_disable)
        self.add_path(ftd_to_config)
        self.add_path(disable_to_ftd)
        self.add_path(config_to_ftd)
        self.add_path(fxos_to_local_mgmt)
        self.add_path(local_mgmt_to_fxos)
        self.add_path(local_mgmt_to_rommon)
        self.add_path(ftd_to_rommon)
        self.add_path(rommon_to_fxos)

        self.add_default_statements(default_statement_list)

    def detect_state(self, spawn, context=AttributeDict()):
        """ Detect the device state and glean the actual state if multiple matches are found.
        """
        state_matches = []
        result = spawn.match
        if result:
            prompt = result.match_output.splitlines()[-1]
            for state in self.states:
                if re.search(state.pattern, prompt):
                    state_matches.append(state)

        spawn.log.debug('statemachine detected state(s): {}'.format(state_matches))
        if len(state_matches) > 1:
            # If the current state is in the detected states, assume we can keep the same state
            # If not, try to glean the actual state
            if self.current_state not in [s.name for s in state_matches]:
                self.glean_state(spawn, state_matches)
        elif len(state_matches) == 1:
            self.update_cur_state(state_matches[0].name)
        else:
            spawn.sendline()
            super().go_to('any', spawn, context)

    def glean_state(self, spawn, possible_states):
        """ Try to figure out the state by sending commands and verifying the matches against known output.
        """
        # Create list of commands to execute
        glean_command_map = {}
        state_patterns = []
        for state in possible_states:
            state_patterns.append(state.pattern)
            glean_data = self.STATE_GLEAN.get(state.name, None)
            if glean_data:
                if glean_data.command in glean_command_map:
                    glean_command_map[glean_data.command][glean_data.pattern] = state
                else:
                    glean_command_map[glean_data.command] = {}
                    glean_command_map[glean_data.command][glean_data.pattern] = state

        if not glean_command_map:
            raise StateMachineError('Unable to detect state, multiple states possible and no glean data available')

        # Execute each glean commnd and check for pattern match
        for glean_cmd in glean_command_map:
            glean_pattern_map = glean_command_map[glean_cmd]
            dialog = Dialog(default_statement_list + [Statement(p) for p in state_patterns])

            spawn.sendline(glean_cmd)
            result = dialog.process(spawn)
            if result:
                output = result.match_output
                for glean_pattern in glean_pattern_map:
                    if re.search(glean_pattern, output):
                        self.update_cur_state(glean_pattern_map[glean_pattern])
                        return

    def go_to(self, to_state, spawn, **kwargs):
        spawn.log.debug('statemachine goto: {} -> {}'.format(self.current_state, to_state))
        super().go_to(to_state, spawn, **kwargs)
        if to_state == 'any' and self.current_state in self.STATE_GLEAN:
            glean_states = [self.get_state(name) for name in self.STATE_GLEAN]
            self.glean_state(spawn, glean_states)
