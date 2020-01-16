__author__ = 'Difu Hu <pyats-support@cisco.com;pyats-support-ext@cisco.com>'

from unicon.plugins.generic import GenericSettings


class SrosSettings(GenericSettings):

    def __init__(self):
        super().__init__()
        self.HA_INIT_EXEC_COMMANDS = []
        self.HA_INIT_CONFIG_COMMANDS = []

        self.DEFAULT_CLI_ENGINE = 'classiccli'

        self.MDCLI_CONFIGURE_DEFAULT_MODE = 'private'
