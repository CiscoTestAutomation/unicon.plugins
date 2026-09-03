"""
Module:
    unicon.plugins.ironware.patterns

Author:
    James Di Trapani <james@ditrapani.com.au> - https://github.com/jamesditrapani

Description:
    This subpackage defines patterns for the Ironware NOS
"""

import re

from unicon.plugins.generic.patterns import GenericPatterns

__author__ = "James Di Trapani <james@ditrapani.com.au>"


class IronWarePatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        # ssh@mlx8>
        self.disable_mode = r'^(.*?)[-\.\w]+@[-\.\w]+>$'

        # ssh@mlx8#
        self.privileged_mode = r'^(.*?)[-\.\w]+@[-\.\w]+#$'

        # ssh@mlx8(config)#
        self.config_mode = r'^(.*?)[-\.\w]+@[-\.\w]+\(config\)#$'
