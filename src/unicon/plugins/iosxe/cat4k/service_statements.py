from unicon.eal.dialogs import Statement
from .patterns import IosXECat4kPatterns
from .settings import IosXECat4kSettings

patterns = IosXECat4kPatterns()
settings = IosXECat4kSettings()


change_rp = Statement(pattern=patterns.restart,
                             action=lambda spawn: spawn.close,
                             loop_continue=False,
                             continue_timer=False)
