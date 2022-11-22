from unicon.eal.dialogs import Statement
from unicon.plugins.fxos.statements import fxos_statements
from unicon.plugins.generic.statements import update_context

from .patterns import AsaFp2kPatterns


patterns = AsaFp2kPatterns()


reload_confirm_stmt = Statement(pattern=patterns.reload_confirm,
                                action='send(y)',
                                args=None,
                                loop_continue=True,
                                continue_timer=False)

broken_pipe_stmt = Statement(pattern=patterns.broken_pipe,
                             action=update_context,
                             args={'console': False},
                             loop_continue=False)

restarting_system_stmt = Statement(pattern=patterns.restarting_system,
                                   action=update_context,
                                   args={'console': True},
                                   loop_continue=True,
                                   continue_timer=True)


reload_statements = [
    reload_confirm_stmt, broken_pipe_stmt, restarting_system_stmt,
    Statement(pattern=patterns.disable_prompt)
]

boot_to_rommon_statements = reload_statements + [
    fxos_statements.boot_interrupt_stmt, Statement(pattern=patterns.rommon_prompt)
]
