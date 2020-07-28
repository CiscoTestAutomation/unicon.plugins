""" State machine for Ftd """

__author__ = "dwapstra"

import re

from unicon.core.errors import SubCommandFailure, StateMachineError
from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Dialog, Statement
from unicon.utils import to_plaintext

from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.generic.patterns import GenericPatterns
from unicon.core.errors import UniconAuthenticationError
from .patterns import FtdPatterns


patterns = FtdPatterns()
generic_statements = GenericStatements()
generic_patterns = GenericPatterns()

password_stmt = generic_statements.password_stmt
escape_char_stmt = generic_statements.escape_char_stmt

SUDO_CRED_NAME = 'sudo'


def connect_module_console(state_machine, spawn, context):
    """ Module console state change handler

    When connecting to the module console, the connection can end up in different states.
    This state change handler is detecting the state and perfoming additional state
    transitions as needed by calling the go_to statemachine service.
    """
    sm = state_machine

    dialog = Dialog([escape_char_stmt])
    dialog += Dialog([Statement(state.pattern, loop_continue=False) for state in sm.states])
    spawn.sendline('connect module %s console' % context.get('_module', 1))
    sm.go_to('any', spawn, timeout=spawn.timeout, dialog=Dialog([escape_char_stmt]))

    if sm.current_state != 'module_console':
        sm.go_to('module_console', spawn,
                                   context=context,
                                   hop_wise=True,
                                   timeout=spawn.timeout)

    # send newline so the state transition can pick up the new state
    spawn.sendline()


def connect_cimc(state_machine, spawn, context):
    spawn.sendline('connect cimc %s' % context.get('_cimc_module', '1/1'))


def change_chassis_scope(state_machine, spawn, context):
    scopes = [s for s in context.get('_scope', "").split('/') if s]
    for scope in scopes:
        spawn.sendline("scope %s" % scope)
        spawn.expect(state_machine.get_state('chassis_scope').pattern)
    spawn.sendline()


def escape_telnet(statemachine, spawn, context):
    spawn.send('~')
    spawn.expect(r'telnet>\s?$', timeout=5)
    spawn.sendline('q')


def sudo_password_handler(spawn, context):
    """ Password handler for sudo command
    Need a better place for 'sudo' password, using line_password as workaround
    """
    credentials = context.get('credentials')
    if credentials:
        try:
            spawn.sendline(
                to_plaintext(credentials[SUDO_CRED_NAME]['password']))
        except KeyError as exc:
            raise UniconAuthenticationError("No password has been defined "
                "for credential '{}'.".format(SUDO_CRED_NAME))
    else:
        spawn.sendline(context['line_password'])


def sudo_failed():
    raise Exception('sudo failed')



class FtdStateMachine(StateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        chassis = State('chassis', patterns.chassis_prompt)
        chassis_scope = State('chassis_scope', patterns.chassis_scope_prompt)
        fxos = State('fxos', patterns.fxos_prompt)
        local_mgmt = State('local-mgmt', patterns.local_mgmt_prompt)
        cimc = State('cimc', patterns.cimc_prompt)
        module_console = State('module_console', patterns.module_console_prompt)
        ftd_console = State('ftd_console', patterns.ftd_console_prompt)
        ftd_expert = State('ftd_expert', patterns.ftd_expert_prompt)
        ftd_expert_root = State('ftd_expert_root', patterns.ftd_expert_root_prompt)

        chassis_to_chassis_scope = Path(chassis, chassis_scope, change_chassis_scope, None)
        chassis_scope_to_chassis = Path(chassis_scope, chassis, 'top', None)

        chassis_to_fxos = Path(chassis, fxos, 'connect fxos', None)
        fxos_to_chassis = Path(fxos, chassis, 'exit', None)

        chassis_to_local_mgmt = Path(chassis, local_mgmt, 'connect local-mgmt', None)
        local_mgmt_to_chassis = Path(local_mgmt, chassis, 'exit', None)

        chassis_to_cimc = Path(chassis, cimc, connect_cimc, None)
        cimc_to_chassis = Path(cimc, chassis, 'exit', None)

        chassis_to_module_console = Path(chassis, module_console, connect_module_console, None)
        module_console_to_chassis = Path(module_console, chassis, escape_telnet, None)

        module_console_to_ftd_console = Path(module_console, ftd_console, 'connect ftd', None)
        ftd_console_to_module_console = Path(ftd_console, module_console, 'exit', None)

        ftd_console_to_ftd_expert = Path(ftd_console, ftd_expert, 'expert', None)
        ftd_expert_to_ftd_console = Path(ftd_expert, ftd_console, 'exit', None)

        ftd_expert_to_ftd_expert_root = Path(ftd_expert, ftd_expert_root, 'sudo su -',
                                                    Dialog([Statement(generic_patterns.password, sudo_password_handler,
                                                                        None, True, False),
                                                            Statement(patterns.sudo_incorrect_password_pattern,
                                                                      sudo_failed)
                                                           ]))
        ftd_expert_root_to_ftd_expert = Path(ftd_expert_root, ftd_expert, 'exit', None)

        self.add_state(chassis)
        self.add_state(chassis_scope)
        self.add_state(fxos)
        self.add_state(local_mgmt)
        self.add_state(cimc)
        self.add_state(module_console)
        self.add_state(ftd_console)
        self.add_state(ftd_expert)
        self.add_state(ftd_expert_root)

        self.add_path(chassis_to_chassis_scope)
        self.add_path(chassis_scope_to_chassis)
        self.add_path(chassis_to_fxos)
        self.add_path(fxos_to_chassis)
        self.add_path(chassis_to_local_mgmt)
        self.add_path(local_mgmt_to_chassis)
        self.add_path(chassis_to_cimc)
        self.add_path(cimc_to_chassis)
        self.add_path(chassis_to_module_console)
        self.add_path(module_console_to_chassis)
        self.add_path(module_console_to_ftd_console)
        self.add_path(ftd_console_to_module_console)
        self.add_path(ftd_console_to_ftd_expert)
        self.add_path(ftd_expert_to_ftd_console)
        self.add_path(ftd_expert_to_ftd_expert_root)
        self.add_path(ftd_expert_root_to_ftd_expert)

