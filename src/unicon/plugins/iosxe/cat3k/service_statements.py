__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"

from unicon.eal.dialogs import Statement
from .patterns import IosXECat3kPatterns
from .setting import IosXECat3kSettings

patterns = IosXECat3kPatterns()
settings = IosXECat3kSettings()


tcpdump_continue = Statement(pattern=patterns.tcpdump,
                             action=lambda spawn: spawn.sendline(""),
                             loop_continue=False,
                             continue_timer=False)
