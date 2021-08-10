
from functools import wraps
from datetime import datetime, timedelta

from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import connection_statement_list
from unicon.plugins.generic.service_statements import (
    save_env, confirm_reset, reload_confirm, reload_confirm_ios)

from ..service_statements import boot_image
from .patterns import IosXECat9kPatterns

patterns = IosXECat9kPatterns()


def boot_finished_deco(func):
    '''Decorator function that wraps dialog statements
    for rommon to disable state transition to pop the
    boot_start_time  after boot is (supposedly) finished.

    Used with rommon_boot_statement_list (see below)
    '''

    @wraps(func)
    def wrapper(spawn, context, session):
        if context:
            context.pop('boot_start_time', None)
            # Todo: dependency injection for handlers
        return func(spawn)
    return wrapper


def boot_timeout_handler(spawn, context, session):
    '''Special handler for dialog timeouts that occur during boot.
    Based on start_boot_time set in the rommon->disable
    transition handler, determine if boot is taking too
    long and raise an exception.
    '''
    boot_timeout_time = timedelta(seconds=spawn.settings.BOOT_TIMEOUT)
    boot_start_time = context.get('boot_start_time')
    if boot_start_time:
        current_time = datetime.now()
        delta_time = current_time - boot_start_time
        if delta_time > boot_timeout_time:
            context.pop('boot_start_time', None)
            raise TimeoutError('Boot timeout')
        return True
    else:
        return False


boot_interrupt_stmt = Statement(
    pattern=patterns.boot_interrupt_prompt,
    action='send(\x03)',
    args=None,
    loop_continue=True,
    continue_timer=False)


boot_timeout_stmt = Statement(
    pattern='__timeout__',
    action=boot_timeout_handler,
    args=None,
    loop_continue=True,
    continue_timer=False)


boot_from_rommon_stmt = Statement(
    pattern=patterns.rommon_prompt,
    action=boot_image,
    args=None,
    loop_continue=True,
    continue_timer=False)


reload_to_rommon_statement_list = [save_env,
                                   confirm_reset,
                                   reload_confirm,
                                   reload_confirm_ios,
                                   boot_interrupt_stmt]


# Create list of statements for rommon to disable, i.e. device boot
# If the boot is completed because we hit a statement with
# loop_continue = False, use the wrapper to pop the start time
# from the context dict.
rommon_boot_statement_list = connection_statement_list.copy()
for stmt in rommon_boot_statement_list:
    if stmt.pattern in [patterns.press_return] or stmt.loop_continue is False:
        stmt.action = boot_finished_deco(stmt.action)
