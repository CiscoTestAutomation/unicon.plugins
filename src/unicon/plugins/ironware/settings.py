"""
Module:
    unicon.plugins.ironware.settings

Author:
    James Di Trapani <james@ditrapani.com.au> - https://github.com/jamesditrapani

Description:
    Define/Override Generic Settings specific to the Ironware NOS
"""

from unicon.plugins.generic.settings import GenericSettings

__author__ = "James Di Trapani <james@ditrapani.com.au>"


class IronWareSettings(GenericSettings):

    def __init__(self):
        # inherit any parent settings
        super().__init__()
        self.CONNECTION_TIMEOUT = 60*5
        self.HA_INIT_EXEC_COMMANDS = ['terminal length 0']
        self.HA_INIT_CONFIG_COMMANDS = []
