
from time import sleep

from unicon.eal.dialogs import Statement
from .service_patterns import ReloadPatterns

def send_response(spawn, response=""):
    sleep(0.5)
    spawn.sendline(response)


pat = ReloadPatterns()

reload_confirm_continue_stmt = Statement(pattern=pat.reload_confirm,
                           action=send_response, args={'response': 'yes'},
                           loop_continue=True,
                           continue_timer=False)

reload_confirm_stmt = Statement(pattern=pat.reload_confirm,
                           action=send_response, args={'response': 'yes'},
                           loop_continue=False,
                           continue_timer=False)

reload_continue_statement_list = [reload_confirm_continue_stmt]

reload_statement_list = [reload_confirm_stmt]
