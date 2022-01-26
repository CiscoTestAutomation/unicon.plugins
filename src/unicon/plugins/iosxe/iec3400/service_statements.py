
from unicon.eal.dialogs import Statement


reload_proceed_stmt = Statement(pattern=r'.*Proceed with reload\?\[y/n]\s*$',
                                action='sendline(y)',
                                loop_continue=True,
                                continue_timer=False)


reload_statement_list = [
    reload_proceed_stmt
]
