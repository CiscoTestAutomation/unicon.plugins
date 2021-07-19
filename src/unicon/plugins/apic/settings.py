""" Defines the settings for aci based unicon connections """

__author__ = "dwapstra"

from unicon.plugins.generic.settings import GenericSettings


class AciSettings(GenericSettings):
    """" Generic platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()
        self.TERM = 'vt100'
        self.HA_INIT_EXEC_COMMANDS = [
            'terminal length 0',
            'terminal width 0'
            ]
        self.HA_INIT_CONFIG_COMMANDS = []
        self.ERROR_PATTERN = [
            r'^(%\s*)?Error',
        ]

        self.POST_RELOAD_WAIT = 330
        self.RELOAD_RECONNECT_ATTEMPTS = 3
        self.RELOAD_TIMEOUT = 420
