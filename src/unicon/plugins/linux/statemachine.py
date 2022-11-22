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

# Used to set the pattern and return the function
def set_update_shell_prompt_pattern(pattern):
    def update_shell_prompt_pattern(statemachine, spawn, context):
        """ After learn_hostname patten match, this state transition updates the shell pattern
        """
        statemachine.get_state('shell').pattern = pattern or p.shell_prompt
        spawn.sendline()
    return update_shell_prompt_pattern


class LinuxStateMachine(StateMachine):
    def __init__(self, settings=None, **kwargs):
        if settings:
            self.prompt = settings.PROMPT if hasattr(settings, 'PROMPT') else None
            self.shell_prompt = settings.SHELL_PROMPT if hasattr(settings, 'SHELL_PROMPT') else None
        super().__init__(**kwargs)

    def create(self):
        self.prompt = self.prompt if hasattr(self, 'prompt') else None
        self.shell_prompt = self.shell_prompt if hasattr(self, 'shell_prompt') else None
        
        shell = State('shell', self.prompt or p.prompt)
        learn_hostname = State('learn_hostname', p.learn_hostname)
        learn_hostname_to_shell = Path(learn_hostname, shell, set_update_shell_prompt_pattern(self.shell_prompt), None)

        self.add_state(shell)

        # the learn_hostname state must be added as the last state entry, this will make it first
        # in the pattern list when using learn_hostname = True.
        self.add_state(learn_hostname)
        self.add_path(learn_hostname_to_shell)
