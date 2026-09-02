""" Generic IOS-XE Quad Service Statements """

from unicon.eal.dialogs import Statement
from unicon.plugins.generic.service_statements import (reload_statement_list,
                                                       switchover_statement_list)

from .patterns import IosXEQuadPatterns

patterns = IosXEQuadPatterns()

def update_rpr_state(spawn, context, state):
    context['state'] = state

# proceed_switchover
proceed_sw = Statement(pattern=patterns.proceed_switchover,
                       action='sendline()',
                       loop_continue=True,
                       continue_timer=False)
# rpr_state
rpr_state = Statement(pattern=patterns.rpr_state,
                      action=update_rpr_state,
                      args={'state': 'rpr'},
                      trim_buffer=False,
                      loop_continue=False,
                      continue_timer=False)
# press_enter
press_enter = Statement(pattern=patterns.press_enter,
                        action='sendline()',
                        loop_continue=False,
                        continue_timer=False)

quad_switchover_stmt_list = list(switchover_statement_list)
quad_switchover_stmt_list.insert(0, proceed_sw)
quad_switchover_stmt_list.insert(0, rpr_state)
quad_switchover_stmt_list.insert(0, press_enter)


quad_reload_stmt_list = list(reload_statement_list)
quad_reload_stmt_list.insert(0, rpr_state)
quad_reload_stmt_list.insert(0, press_enter)