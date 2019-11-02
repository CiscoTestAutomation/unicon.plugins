
from unicon.statemachine import Path, State, StateMachine
from .patterns import AireosPatterns


p = AireosPatterns()


class AireosStateMachine(StateMachine):
    def create(self):

        enable = State('enable', p.prompt + '>')
        show = State('show', p.prompt + 'show>')
        config = State('config', p.prompt + 'config>')

        enable_to_show = Path(enable, show, 'show', None)
        enable_to_config = Path(enable, config, 'config', None)
        config_to_enable = Path(config, enable, 'exit', None)

        self.add_state(enable)
        self.add_state(show)
        self.add_state(config)

        self.add_path(enable_to_show)
        self.add_path(enable_to_config)
        self.add_path(config_to_enable)

        # TODO: find how to remove pseudo state
        generic = State('generic', 'dummy')
        generic_to_enable = Path(generic, enable, '', None)
        self.add_state(generic)
        self.add_path(generic_to_enable)
