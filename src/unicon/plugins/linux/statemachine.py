"""
Module:
    unicon.plugins.linux.statemachine

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    This subpackage implements state machine for linux Linux
"""

from unicon.statemachine import State, Path, StateMachine
from unicon.plugins.linux.patterns import LinuxPatterns

p = LinuxPatterns()

def update_shell_prompt_pattern(statemachine, spawn, context):
    """ After learn_hostname patten match, this state transition updates the shell pattern
    """
    statemachine.get_state('shell').pattern = p.shell_prompt
    spawn.sendline()


class LinuxStateMachine(StateMachine):
    def create(self):
        shell = State('shell', p.prompt)
        learn_hostname = State('learn_hostname', p.learn_hostname)

        learn_hostname_to_shell = Path(learn_hostname, shell, update_shell_prompt_pattern, None)

        self.add_state(shell)

        # the learn_hostname state must be added as the last state entry, this will make it first
        # in the pattern list when using learn_hostname = True.
        self.add_state(learn_hostname)
        self.add_path(learn_hostname_to_shell)
