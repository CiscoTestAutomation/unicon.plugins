""" Defines the settings for ConfD/CSP based unicon connections """

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


from ..settings import ConfdSettings


class CspSettings(ConfdSettings):
    """" Generic platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()
        self.CISCO_INIT_EXEC_COMMANDS = []
        self.CISCO_INIT_CONFIG_COMMANDS = [
            'session paginate false'
        ]

        self.RELOAD_TIMEOUT = 600
