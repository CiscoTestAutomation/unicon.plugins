
from unicon.eal.dialogs import Statement
from unicon.plugins.generic.service_statements import (
    save_env, confirm_reset, reload_confirm, reload_confirm_ios)

from .patterns import IosXECat9kPatterns

patterns = IosXECat9kPatterns()


boot_interrupt_stmt = Statement(
    pattern=patterns.boot_interrupt_prompt,
    action='send(\x03)',
    args=None,
    loop_continue=True,
    continue_timer=False)


reload_to_rommon_statement_list = [save_env,
                                   confirm_reset,
                                   reload_confirm,
                                   reload_confirm_ios,
                                   boot_interrupt_stmt]
