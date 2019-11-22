__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.statemachine import State, Path

from unicon.plugins.iosxe.statemachine import IosXESingleRpStateMachine

from .patterns import IosXECsr1000vPatterns

patterns = IosXECsr1000vPatterns()


class IosXECsr1000vSingleRpStateMachine(IosXESingleRpStateMachine):
    def create(self):
        super().create()

        self.remove_path('enable', 'rommon')
        self.remove_path('rommon', 'disable')
        self.remove_state('rommon')

        # Saw the following line in the CSR1000V log that led to a
        # match failure, so relaxing the config_prompt.
        # Router(config-line)#tion generated from file cdrom1:/ovf-env.xml
        self.remove_path('enable', 'config')
        self.remove_path('config', 'enable')
        self.remove_state('config')

        config = State('config', patterns.config_prompt)
        enable = [state for state in self.states if state.name == 'enable'][0]
        enable_to_config = Path(enable, config, self.config_command, None)
        config_to_enable = Path(config, enable, 'end', None)
        self.add_state(config)
        self.add_path(enable_to_config)
        self.add_path(config_to_enable)
