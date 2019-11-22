__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.plugins.iosxr.statemachine import IOSXRSingleRpStateMachine
from unicon.plugins.iosxr.statemachine import IOSXRDualRpStateMachine

from unicon.plugins.iosxr.asr9k.patterns import IOSXRAsr9kPatterns
from unicon.plugins.iosxr.statements import IOSXRStatements
from unicon.statemachine import State, Path
from unicon.eal.dialogs import Statement, Dialog


patterns = IOSXRAsr9kPatterns()
statements = IOSXRStatements()


class IOSXRASR9KSingleRpStateMachine(IOSXRSingleRpStateMachine):
    pass


class IOSXRASR9KDualRpStateMachine(IOSXRDualRpStateMachine):
    pass
