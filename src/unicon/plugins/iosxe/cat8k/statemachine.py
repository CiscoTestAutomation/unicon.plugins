__author__ = "Lukas McClelland <lumcclel@cisco.com>"

from unicon.plugins.iosxe.statemachine import IosXESingleRpStateMachine


class IosXECat8kSingleRpStateMachine(IosXESingleRpStateMachine):
    def create(self):
        super().create()

