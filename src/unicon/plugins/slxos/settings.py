"""
Module:
    unicon.plugins.slxos
Author:
    Fabio Pessoa Nunes (https://www.linkedin.com/in/fpessoanunes/)
Description:
  This module defines the Slxos settings to setup
  the unicon environment required for generic based
  unicon connection
"""

from unicon.plugins.generic import GenericSettings


class SlxosSettings(GenericSettings):
    """" Slxos platform settings """

    def __init__(self):
        super().__init__()
        self.HA_INIT_EXEC_COMMANDS = [
            'terminal length 0',
            'terminal timeout 0',
            'no terminal monitor',
            'show version'
        ]
        self.HA_INIT_CONFIG_COMMANDS = []
