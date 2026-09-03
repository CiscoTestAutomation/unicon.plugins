""" Defines the settings for staros based unicon connections """

__author__ = "dwapstra"

from unicon.plugins.generic.settings import GenericSettings


class StarosSettings(GenericSettings):
    """" Generic platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()

        self.HA_INIT_EXEC_COMMANDS = [
            'terminal length 0',
            'terminal width 512',
            'no timestamps'
        ]
        self.HA_INIT_CONFIG_COMMANDS = []

        self.ERROR_PATTERN = [
            r'^Failure:',
        ]

