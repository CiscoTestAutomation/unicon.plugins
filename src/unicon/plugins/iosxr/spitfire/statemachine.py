__author__ = "Sritej K V R <skanakad@cisco.com>"

from unicon.plugins.iosxr.statemachine import IOSXRSingleRpStateMachine
from unicon.plugins.iosxr.spitfire.patterns import SpitfirePatterns
from unicon.plugins.iosxr.spitfire.statements import SpitfireStatements
from unicon.statemachine import State, Path
from unicon.core.errors import StateMachineError
from unicon.eal.dialogs import Statement, Dialog
from unicon.utils import AttributeDict
import time

patterns = SpitfirePatterns()
statements = SpitfireStatements()


login_dialog = Dialog([statements.bmc_login_stmt,
                       statements.password_stmt,
                       statements.login_stmt
                       ])



def switch_console(statemachine, spawn, context):
    sm = statemachine
    # switch between XR and BMC console
    if sm.current_state == 'enable':
        target_state = 'bmc'
    elif sm.current_state == 'bmc':
        target_state = 'enable'
    else:
        raise StateMachineError('Unsupported state transition from {}'.format(sm.current_state))

    # Try ctrl-o (\x0f) and then ctrl-w (\x17)
    for cmd in ['\x0f', '\x17']:
        spawn.send(cmd)
        sm.go_to('any', spawn, timeout=spawn.timeout ,context=context, dialog=login_dialog)
        if sm.current_state == target_state:
            spawn.sendline()
            return

    raise StateMachineError('Unable to switch console state')



class SpitfireSingleRpStateMachine(IOSXRSingleRpStateMachine):
    def __init__(self, hostname=None):
        super().__init__(hostname)


    def create(self):
        bmc = State('bmc', patterns.bmc_prompt)
        xr = State('enable',patterns.enable_prompt)
        xr_config = State('config',patterns.config_prompt)
        xr_bash = State ('xr_bash',patterns.xr_bash_prompt)
        xr_run = State('xr_run',patterns.xr_run_prompt)
        xr_env = State ('xr_env', patterns.xr_env_prompt)

        self.add_state(bmc)
        self.add_state(xr)
        self.add_state(xr_config)
        self.add_state(xr_bash)
        self.add_state(xr_run)
        self.add_state(xr_env)

        config_dialog = Dialog([
           [patterns.commit_changes_prompt, 'sendline(yes)', None, True, False],
           [patterns.commit_replace_prompt, 'sendline(yes)', None, True, False],
           [patterns.configuration_failed_message,
           'sendline(show configuration failed)', None, True, False]
           ])

        xr_to_bmc = Path(xr, bmc, switch_console, login_dialog)
        self.add_path(xr_to_bmc)
        xr_bash_to_bmc = Path(xr_bash, bmc, switch_console, login_dialog)
        self.add_path(xr_bash_to_bmc)

        bmc_to_xr = Path(bmc, xr, switch_console, login_dialog)
        self.add_path(bmc_to_xr)

        xr_to_xr_bash = Path(xr, xr_bash, "bash" , None)
        self.add_path(xr_to_xr_bash)
        xr_bash_to_xr = Path(xr_bash, xr, "exit", login_dialog)
        self.add_path(xr_bash_to_xr)

        xr_to_xr_run = Path(xr, xr_run, "run" , None)
        self.add_path(xr_to_xr_run)
        xr_run_to_xr = Path(xr_run, xr, "exit", login_dialog)
        self.add_path(xr_run_to_xr)

        xr_to_xr_config = Path(xr, xr_config, 'configure terminal', None)
        self.add_path(xr_to_xr_config)
        xr_config_to_xr = Path(xr_config, xr, 'end', config_dialog)
        self.add_path(xr_config_to_xr)

        xr_bash_to_xr_env = Path(xr_bash, xr_env, "xrenv", None)
        self.add_path(xr_bash_to_xr_env)
        xr_env_to_xr_bash = Path(xr_env, xr_bash, "exit", None)
        self.add_path(xr_env_to_xr_bash)

        xr_run_to_xr_env = Path(xr_run, xr_env, "xrenv", None)
        self.add_path(xr_run_to_xr_env)
        xr_env_to_xr_run = Path(xr_env, xr_run, "exit", None)
        self.add_path(xr_env_to_xr_run)

        self.add_default_statements(self.default_commands)


class SpitfireDualRpStateMachine(SpitfireSingleRpStateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        super().create()

        standby_locked = State('standby_locked', patterns.standby_prompt)
        self.add_state(standby_locked)
