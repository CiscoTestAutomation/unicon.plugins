__author__ = "Dave Wapstra <dwapstra@cisco.com>"

from unicon.bases.routers.connection import BaseSingleRpConnection

from .viptela import ViptelaSingleRPConnection


class SDWANConnection(ViptelaSingleRPConnection):
    os = 'viptela'
    platform = None
    chassis_type = 'single_rp'
