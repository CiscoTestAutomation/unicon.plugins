'''
Author: Sam Johnson
Contact: samuel.johnson@gmail.com
https://github.com/TestingBytes

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example

Description:
    This subpackage defines patterns for Check Point Gaia OS
'''

from unicon.plugins.generic.patterns import GenericPatterns


class GaiaPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()

        # This system is for authorized use only.
        # login: admin
        # Password:
        self.login_prompt = r'^(.*?)login:\s*$'
        self.password_prompt = r'^(.*?)Password:\s*$'

        # Last login: Tue Mar 23 22:11:15 on ttyS0
        # hostname>
        self.clish_prompt = r'^(.*?)%N>\s*$'

        # hostname> expert
        # Enter expert password:
        self.expert_password_prompt = r'^(.*?)Enter expert password:\s*$'

        # hostname> expert
        # Enter expert password:
        #
        # Wrong password.
        self.expert_password_failed = r'^(.*?)Wrong password\.\s*$'

        # Warning! All configurations should be done through clish
        # You are in expert mode now.
        # [Expert@hostname:0]#
        self.expert_prompt = r'^(.*?)\[\w+\@%N\:\d?\]#\s*$'
