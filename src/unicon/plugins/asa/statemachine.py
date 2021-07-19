from unicon.statemachine import Path, State, StateMachine

from unicon.plugins.generic.statements import default_statement_list

from unicon.plugins.asa import statements, patterns
from unicon.eal.dialogs import Dialog


class ASAStateMachine(StateMachine):
    def create(self):
        p = patterns.ASAPatterns()

        enable = State('enable', p.enable_prompt)
        disable = State('disable', p.disable_prompt)
        config = State('config', p.config_prompt)

        enable_to_disable = Path(enable, disable, 'disable', None)
        enable_to_config = Path(enable, config, 'config term', None)

        disable_to_enable = Path(disable, enable, 'enable',
                                 Dialog([statements.enable_password]))

        config_to_enable = Path(config, enable, 'end', None)

        self.add_state(enable)
        self.add_state(disable)
        self.add_state(config)

        self.add_path(enable_to_disable)
        self.add_path(enable_to_config)
        self.add_path(config_to_enable)
        self.add_path(disable_to_enable)

        self.add_default_statements(default_statement_list)
