"""
Module:
    unicon.plugins.hvrp
Authors:
    Miguel Botia (mibotiaf@cisco.com), Leonardo Anez (leoanez@cisco.com)
Description:
    This module defines the HVRP settings to setup the unicon environment required for generic based unicon connection.
"""

from unicon.plugins.generic import GenericSettings


class HvrpSettings(GenericSettings):
    """" Hvrp platform settings """

    def __init__(self):
        super().__init__()
        self.HA_INIT_EXEC_COMMANDS = [
            'screen-length 0 temporary',
            'undo terminal alarm',
            'undo terminal logging',
            'undo terminal debugging',
            'undo terminal monitor'
        ]

        self.HA_INIT_CONFIG_COMMANDS = []
        self.ERROR_PATTERN.append("Error:.*")
        self.CONFIGURE_ERROR_PATTERN.append(r'^Error:.*')
