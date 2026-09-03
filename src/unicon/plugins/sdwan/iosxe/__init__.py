__author__ = "Dave Wapstra <dwapstra@cisco.com>"

import warnings
from unicon.plugins.iosxe.sdwan import SDWANSingleRpConnection


class SDWANConnection(SDWANSingleRpConnection):
    os = 'sdwan'
    platform = 'iosxe'

    def __init__(self, *args, **kwargs):
        warnings.warn(message = "This plugin is deprecated and replaced by 'iosxe/sdwan'",
                      category = DeprecationWarning)
        super().__init__(*args, **kwargs)
