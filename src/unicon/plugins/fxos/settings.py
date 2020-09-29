""" Defines the settings for fxos based unicon connections """

__author__ = "dwapstra"

from unicon.plugins.generic.settings import GenericSettings


class FxosSettings(GenericSettings):
    """" Generic platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()

        self.HA_INIT_EXEC_COMMANDS = []
        self.HA_INIT_CONFIG_COMMANDS = []

        self.TERM = 'vt100'
        self.ERROR_PATTERN = [
            r'^Error:',
            r'^%\s*[Ii]nvalid [Cc]ommand',
            r"^%\s*Ambiguous command at '\^' marker"
        ]
