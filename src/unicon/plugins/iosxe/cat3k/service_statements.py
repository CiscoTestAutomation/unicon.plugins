__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"

from ..service_statements import boot_image
from unicon.eal.dialogs import Statement
from .patterns import IosXECat3kPatterns
from .setting import IosXECat3kSettings

patterns = IosXECat3kPatterns()
settings = IosXECat3kSettings()


boot_reached = Statement(pattern=patterns.rommon_prompt,
                         action=boot_image,
                         loop_continue=True,
                         continue_timer=False)

access_shell = Statement(pattern=patterns.access_shell,
                         action=lambda spawn: spawn.sendline("y"),
                         loop_continue=True,
                         continue_timer=False)

tcpdump_continue = Statement(pattern=patterns.tcpdump,
                             action=lambda spawn: spawn.sendline(""),
                             loop_continue=False,
                             continue_timer=False)
