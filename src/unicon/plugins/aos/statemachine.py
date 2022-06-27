'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson and Cisco Development Team:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.statemachine import State, Path, StateMachine
from unicon.eal.dialogs import Statement, Dialog
from unicon.plugins.aos.patterns import aosPatterns
patterns = aosPatterns()

class aosSingleRpStateMachine(StateMachine):

    def create(self):
        '''
        statemachine class's create() method is its entrypoint. This showcases
        how to setup a statemachine in Unicon. 
        '''

        ##########################################################
        # State Definition
        ##########################################################
        shell = State('shell', r'\#$')
        enable = State('enable', patterns.enable_prompt)
        config = State('config', patterns.config_prompt)
        proxy = State('proxy', patterns.proxy)
        generic = State('Generic', patterns.generic)
        enter = State('enter', patterns.press_any_key_
        ##########################################################
        # Path Definition
        ##########################################################

        enable_to_shell = Path(enable, shell, command='enable', dialog=None)
        shell_to_enable = Path(shell, enable, command='exit', dialog=None)
        enter_to_enable = Path(enter, enable, commands= '\r', dialog=None)
        enable_to_config = Path(enable, config, command='configure', dialog=None)
        config_to_enable = Path(config, enable, command='exit', dialog=None)

        #proxy_to_shell = Path(proxy, shell, None , None)
        #shell_to_proxy = Path(shell, proxy, None, None)
        # Add State and Path to State Machine
        self.add_state(shell)
        self.add_state(enable)
        self.add_state(config)
        self.add_state(proxy)
        self.add_state(generic)
        self.add_state()
        self.add_path(enable_to_shell)
        self.add_path(shell_to_enable)

        self.add_path(enable_to_config)
        self.add_path(config_to_enable)

        #self.add_path(proxy_to_shell)
        #self.add_path(shell_to_proxy)
