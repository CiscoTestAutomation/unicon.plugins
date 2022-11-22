__author__ = "dwapstra"

from ..settings import IOSXRSettings

class NCS5KSettings(IOSXRSettings):
    def __init__(self):
        super().__init__()

        # prompt wait delay
        self.ESCAPE_CHAR_PROMPT_WAIT = 10

        # prompt wait retries
        self.ESCAPE_CHAR_PROMPT_WAIT_RETRIES = 3

        # number of retries to reconnect after reloading
        self.RELOAD_RECONNECT_ATTEMPTS = 3
        
        self.STANDBY_STATE_REGEX = r'Standby node .* is (.*)'
