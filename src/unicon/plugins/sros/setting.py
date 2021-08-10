__author__ = 'Difu Hu <pyats-support@cisco.com;pyats-support-ext@cisco.com>'

from unicon.plugins.generic import GenericSettings


class SrosSettings(GenericSettings):

    def __init__(self):
        super().__init__()
        self.DEFAULT_CLI_ENGINE = 'classiccli'

        self.MDCLI_CONFIGURE_DEFAULT_MODE = 'private'

        self.MD_INIT_EXEC_COMMANDS = [
            'environment console length 512',
            'environment console width 512'
        ]
        self.MD_INIT_CONFIG_COMMANDS = []

        self.CLASSIC_INIT_EXEC_COMMANDS = [
            'environment no more',
            'environment no saved-ind-prompt'
        ]
        self.CLASSIC_INIT_CONFIG_COMMANDS = []

        self.DEFAULT_LEARNED_HOSTNAME = r'([^@# \t\n\r\f\v]+)'
