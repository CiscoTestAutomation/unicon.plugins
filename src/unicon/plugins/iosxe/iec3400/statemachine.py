
from unicon.plugins.generic.service_statements import generic_statements

from unicon.plugins.iosxe.statemachine import IosXESingleRpStateMachine


class IosXEIec3400SingleRpStateMachine(IosXESingleRpStateMachine):

    def create(self):
        super().create()
        config_to_enable = self.get_path('config', 'enable')
        config_to_enable.command = 'exit'

        self.add_default_statements([generic_statements.terminal_position_stmt])
