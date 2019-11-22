__author__ = 'Difu Hu <difhu@cisco.com>'

from unicon.eal.dialogs import Statement
from unicon.plugins.generic.service_statements import ha_reload_statement_list

from .service_patterns import IosIolHaReloadPatterns

patterns = IosIolHaReloadPatterns()

reload_switch = Statement(pattern=patterns.reload_switch_prompt,
                          action='sendline()',
                          args=None,
                          loop_continue=True,
                          continue_timer=True)

ios_iol_ha_reload_statement_list = ha_reload_statement_list + [reload_switch]
