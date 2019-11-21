__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon_plugins.plugins.iosxe.sdwan import SDWANSingleRpConnection

class SDWANConnection(SDWANSingleRpConnection):
    os = 'sdwan'
    series = 'iosxe'
