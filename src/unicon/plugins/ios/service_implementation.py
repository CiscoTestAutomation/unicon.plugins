""" Generic IOS service implementations. """

__author__ = "Sanjana Bhutani"

from unicon.plugins.generic.service_implementation import \
    Ping as GenericPing

class Ping(GenericPing):
    def call_service(self, addr, command="", *, vrf=None, **kwargs):
        command = command if command else \
            "ping vrf {vrf}".format(vrf=vrf) if vrf else "ping"
        super().call_service(addr=addr, command=command, **kwargs)
