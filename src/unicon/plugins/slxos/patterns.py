"""
Module:
    unicon.plugins.slxos
Authors:
    Fabio Pessoa Nunes (https://www.linkedin.com/in/fpessoanunes/)
Description:
    Module for defining all the Patterns required for the
    Slxos implementation
"""

from unicon.plugins.generic.patterns import GenericPatterns


class SlxosPatterns(GenericPatterns):
    """
        Class defines all the patterns required
        for Slxos
    """
    def __init__(self):
        super().__init__()

        self.default_hostname_pattern = r'SLX'
        self.username = r'^.*[Ll]ogin:\s*$'
        self.password = r'^.*[Pp]assword:\s*$'
        # SLX#
        self.enable_prompt = r'^(.*?)(.*|%N|SLX)#\s*$'
        # SLX(config)#
        self.config_prompt = r'^\S+\(config\)#\s*$'
        self.save_confirm = r'This operation will (back up the current|modify your startup) configuration\. Do you want to continue\? \[y/n\]:\s*$'
