'''
Author: Renato Almeida de Oliveira
Contact: renato.almeida.oliveira@gmail.com
https://twitter.com/ORenato_Almeida
https://www.youtube.com/c/RenatoAlmeidadeOliveira
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.statemachine import State, Path
from unicon.plugins.comware.patterns import HPComwarePatterns
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine


patterns = HPComwarePatterns()


class HPComwareSingleRpStateMachine(GenericSingleRpStateMachine):
    """
        Defines HP Comware StateMachine for singleRP
        Statemachine keeps in track all the supported states
        for this platform, also have detail about moving from
        one state to another
    """
    def create(self):
        """creates the hp comware state machine"""

        super().create()
        ##########################################################
        # Remove unused paths and state
        ##########################################################
        self.remove_path('enable', 'rommon')
        self.remove_path('rommon', 'disable')
        self.remove_path('disable', 'enable')
        
        self.remove_state('rommon')
        self.remove_state('disable')
        ##########################################################
        # Remove replaced states and paths
        ##########################################################
        self.remove_path('enable','config')
        self.remove_path('config','enable')
    
        self.remove_state('enable')
        self.remove_state('config')
        ##########################################################
        # State Definition
        ##########################################################
        enable = State('enable', patterns.user_exec_mode)
        config = State('config', patterns.config_mode)
        ##########################################################
        # Path Definition
        ##########################################################

        enable_to_config = Path(enable, config, 'system-view', None)
        config_to_enable = Path(config, enable, 'return', None)

        # Add State and Path to State Machine
        self.add_state(enable)
        self.add_state(config)

        self.add_path(enable_to_config)
        self.add_path(config_to_enable)
