from time import sleep
from unicon.eal.dialogs import Statement
from unicon.core.errors import SubCommandFailure, CopyBadNetworkError
#from unicon.plugins.generic.service_patterns import ReloadPatterns, \
#    PingPatterns, TraceroutePatterns, CopyPatterns, HaReloadPatterns, \
#    SwitchoverPatterns, ResetStandbyPatterns
from unicon.plugins.generic.service_statements import reload_statement_list
from unicon.plugins.asa.patterns import ASAPatterns 

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#           Service handlers
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def send_response(spawn, response=""):
    sleep(0.5)
    spawn.sendline(response)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Reload  Statements
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

pat = ASAPatterns()

disable_prompt_stmt = Statement(pattern=pat.disable_prompt,
                          action=None,
                          args=None,
                          loop_continue=False,
                          continue_timer=False)
asa_reload_stmt_list = reload_statement_list[:]
asa_reload_stmt_list.append(disable_prompt_stmt)

