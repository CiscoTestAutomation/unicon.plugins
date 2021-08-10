__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.statemachine import State, Path

from unicon.plugins.iosxe.statemachine import IosXESingleRpStateMachine

from .patterns import IosXECsr1000vPatterns

patterns = IosXECsr1000vPatterns()


class IosXECsr1000vSingleRpStateMachine(IosXESingleRpStateMachine):
    def create(self):
        super().create()

