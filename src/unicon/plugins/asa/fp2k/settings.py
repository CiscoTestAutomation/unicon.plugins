__author__ = "dwapstra"

from unicon.plugins.fxos.settings import FxosSettings


class AsaFp2kSettings(FxosSettings):
    """" Generic platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()
        self.HA_INIT_EXEC_COMMANDS = []
        self.HA_INIT_CONFIG_COMMANDS = []

        self.ERROR_PATTERN = [
            r'^%?\s*?Syntax error:',
            r'^\s*?% Invalid command'
        ]

        self.PROMPT_RECOVERY_COMMANDS = ['\x01\x0b', '\r', '\x03', '\r']
