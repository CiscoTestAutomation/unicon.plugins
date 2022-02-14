
import re

from unicon.plugins.iosxe.c9800.statemachine import IosXEc9800SingleRpStateMachine
from unicon.statemachine import State, Path
from unicon.eal.dialogs import Dialog, Statement
from unicon.utils import AttributeDict
from unicon.core.errors import StateMachineError

from unicon.plugins.generic.statements import GenericStatements, default_statement_list

from .service_statements import enter_ap_shell_statement_list, ap_enable_stmt
from .patterns import IosXEEWCGenericPatterns
from .settings import IosXEEWCAPShellSettings


statements = GenericStatements()

patterns = IosXEEWCGenericPatterns()
ap_shell_settings = IosXEEWCAPShellSettings()


def enable_to_ap_disable_transition(statemachine, spawn, context):
    credentials = context.get('credentials') or {}
    command = "wireless ewc-ap ap shell username {}".format(
        credentials.get('ap', {}).get('username', ''))
    spawn.sendline(command)



class IosXEEwcSingleRpStateMachine(IosXEc9800SingleRpStateMachine):

    STATE_GLEAN = AttributeDict({
        'disable': AttributeDict(dict(
            command='show version | inc ^Cisco',
            pattern=patterns.iosxe_glean_pattern)),
        'enable': AttributeDict(dict(
            command='show version | inc ^Cisco',
            pattern=patterns.iosxe_glean_pattern)),
        'ap_disable': AttributeDict(dict(
            command='show version | inc ^Cisco',
            pattern=patterns.ap_glean_pattern)),
        'ap_enable': AttributeDict(dict(
            command='show version | inc ^Cisco',
            pattern=patterns.ap_glean_pattern))
    })

    def create(self):
        super().create()

        enable = self.get_state('enable')

        ap_disable = State('ap_disable', pattern=patterns.ap_disable_prompt)
        ap_enable = State('ap_enable', pattern=patterns.ap_enable_prompt)

        self.add_state(ap_disable)
        self.add_state(ap_enable)

        ap_disable_to_ap_enable = Path(ap_disable, ap_enable, 'enable', Dialog([
            ap_enable_stmt,
            statements.bad_password_stmt,
            statements.syslog_stripper_stmt
        ]))

        ap_disable_to_enable = Path(ap_disable, enable, 'exit', None)
        ap_enable_to_enable = Path(ap_enable, enable, 'exit', None)
        enable_to_ap_disable = Path(enable, ap_disable, enable_to_ap_disable_transition,
            Dialog(enter_ap_shell_statement_list))

        self.add_path(ap_disable_to_ap_enable)
        self.add_path(ap_disable_to_enable)
        self.add_path(ap_enable_to_enable)
        self.add_path(enable_to_ap_disable)

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
