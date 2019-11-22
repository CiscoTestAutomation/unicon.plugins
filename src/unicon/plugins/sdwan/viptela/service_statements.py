
from time import sleep

from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import GenericStatements

from .service_patterns import ReloadPatterns


statements = GenericStatements()
pat = ReloadPatterns()

def reboot_confirm(spawn):
    sleep(0.1)
    spawn.sendline('yes')
    spawn.expect([r'.+$'], timeout=10)


factory_reset_stmt = Statement(pattern=pat.factory_reset_prompt,
                               action=reboot_confirm,
                               loop_continue=False,
                               continue_timer=False)

factory_reset_continue_stmt = Statement(pattern=pat.factory_reset_prompt,
                               action=reboot_confirm,
                               loop_continue=True,
                               continue_timer=True)

reboot_stmt = Statement(pattern=pat.reboot_prompt,
                                action=reboot_confirm,
                                loop_continue=False,
                                continue_timer=False)

reboot_continue_stmt = Statement(pattern=pat.reboot_prompt,
                                action=reboot_confirm,
                                loop_continue=True,
                                continue_timer=True)

system_ready_stmt = Statement(pattern=pat.system_ready,
                              action='sendline()',
                              loop_continue=False,
                              continue_timer=True)

# Respond to prompts and return
reload_statement_list = [reboot_stmt,
                         factory_reset_stmt]

# Respond to prompts and continue loop until system ready
reload_ready_statement_list = [reboot_continue_stmt,
                                  factory_reset_continue_stmt,
                                  system_ready_stmt]

