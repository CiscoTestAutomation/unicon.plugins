""" Defines the settings for cimc based unicon connections """

__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon.plugins.generic.settings import GenericSettings


class CimcSettings(GenericSettings):
    """" Generic platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()
        self.HA_INIT_EXEC_COMMANDS = []
        self.HA_INIT_CONFIG_COMMANDS = []