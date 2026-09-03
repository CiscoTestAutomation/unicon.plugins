""" Defines the settings for aci based unicon connections """

__author__ = "dwapstra"

from ..setting import NxosSettings


class AciSettings(NxosSettings):
    """" Generic platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()
        self.TERM = 'vt100'
        self.HA_INIT_EXEC_COMMANDS = []
        self.HA_INIT_CONFIG_COMMANDS = []
        self.ESCAPE_CHAR_PROMPT_WAIT = 1
        self.POST_RELOAD_WAIT = 30

        self.ENV = {
            'ROWS': 24,
            'COLUMNS': 255
        }
