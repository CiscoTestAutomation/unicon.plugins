__author__ = "Isobel Ormiston <iormisto@cisco.com>"

from unicon.plugins.iosxr.statemachine import IOSXRSingleRpStateMachine
from unicon.plugins.iosxr.moonshine.patterns import MoonshinePatterns 
from unicon.plugins.iosxr.moonshine.statements import MoonshineStatements
from unicon.statemachine import State, Path
from unicon.eal.dialogs import Statement, Dialog


patterns = MoonshinePatterns()
statements = MoonshineStatements()


class MoonshineSingleRpStateMachine(IOSXRSingleRpStateMachine):
    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        shell = State('shell', patterns.shell_prompt)
        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)

        self.add_state(shell)
        self.add_state(enable)
        self.add_state(config)

        shell_dialog = Dialog([[patterns.shell_prompt, 'sendline(exec)', None, True, False]])

        config_dialog = Dialog([
           [patterns.commit_changes_prompt, 'sendline(yes)', None, True, False],
           [patterns.commit_replace_prompt, 'sendline(yes)', None, True, False],
           [patterns.configuration_failed_message, self.handle_failed_config, 
            None, True, False]
           ])

        shell_to_enable = Path(shell, enable, 'exec', None)
        enable_to_config = Path(enable, config, 'configure terminal', None)
        config_to_enable = Path(config, enable, 'end', config_dialog)
  
        self.add_path(shell_to_enable)
        self.add_path(enable_to_config)
        self.add_path(config_to_enable)

        self.add_default_statements(self.default_commands)


class MoonshineDualRpStateMachine(MoonshineSingleRpStateMachine):

    def __init__(self, hostname=None):
        super().__init__(hostname)

    def create(self):
        super().create()
        
        standby_locked = State('standby_locked', patterns.standby_prompt)
        self.add_state(standby_locked)
         
         
