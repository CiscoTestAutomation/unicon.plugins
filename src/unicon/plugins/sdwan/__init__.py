__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon.bases.routers.connection import BaseSingleRpConnection

class SDWANConnection(BaseSingleRpConnection):
    os = 'sdwan'
    chassis_type = 'single_rp'

    def __init__(self, *args, **kwargs):
        raise NotImplementedError('SDWAN plugin needs specified series "viptela" or "iosxe"')
