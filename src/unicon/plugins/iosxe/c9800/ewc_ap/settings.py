"""Settings relevant to the iosxe/ewc Unicon plugin

Copyright (c) 2019-2020 by cisco Systems, Inc.
All rights reserved.
"""

from unicon.plugins.cheetah.ap.settings import ApSettings
from unicon.plugins.iosxe.settings import IosXESettings


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Bash Shell Settings
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
class IosXEEWCBashShellSettings(IosXESettings):
    def __init__(self):
        super().__init__()


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# AP Shell Settings
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
class IosXEEWCAPShellSettings(ApSettings):

    def __init__(self):
        super().__init__()
        self.EWC_SHORT_UNICON_SLEEP = 0.1
        self.EWC_ENTER_AP_SHELL_TIMEOUT = 20
        self.EWC_AP_TIMEOUT = self.CONSOLE_TIMEOUT + self.EWC_ENTER_AP_SHELL_TIMEOUT
