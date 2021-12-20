__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"

from unicon.plugins.iosxe.statemachine import IosXESingleRpStateMachine
from .patterns import IosXECat3kPatterns
from unicon.statemachine import State, Path
from unicon.eal.dialogs import Dialog

patterns = IosXECat3kPatterns()


class IosXECat3kSingleRpStateMachine(IosXESingleRpStateMachine):
    def create(self):
        super().create()
