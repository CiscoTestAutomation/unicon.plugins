"""
Module:
    unicon.plugins.sonic

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
  This module defines the SONiC settings to setup
  the unicon environment required for SONiC based
  unicon connection
"""
from unicon.plugins.linux.settings import LinuxSettings


class SonicSettings(LinuxSettings):
    """" Linux platform settings """
    def __init__(self):
        """ initialize
        """
        super().__init__()

        # Default error pattern
        self.ERROR_PATTERN.extend([
            r'^Error: No such command .*$',
            r'^Error: Too many matches: .*$'
        ])
