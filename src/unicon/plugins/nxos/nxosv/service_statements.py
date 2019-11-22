from unicon.eal.dialogs import Statement
from unicon.plugins.generic.service_statements import login_handler
from unicon.plugins.generic.service_statements import password_handler

from .service_patterns import NxosvReloadPatterns

from ..service_statements import additional_connection_dialog\
    as nxos_additional_connection_dialog

# Additional statement specific to nxosv
pat = NxosvReloadPatterns()

login_stmt = Statement(pattern=pat.username,
                       action=login_handler,
                       args=None,
                       loop_continue=True,
                       continue_timer=False)

password_stmt = Statement(pattern=pat.password,
                          action=password_handler,
                          args=None,
                          loop_continue=False,
                          continue_timer=False)

additional_connection_dialog = [login_stmt, password_stmt]
