"""
Module:
    unicon.plugins.generic
Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)
Description:
    Module for defining all Services Statement, handlers(callback) and Statement
    list for service dialog would be defined here.
"""

from time import sleep

from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import  chatty_term_wait
from .service_patterns import APReloadPatterns
from unicon.plugins.generic.service_statements import reload_statement_list

pat = APReloadPatterns()


def send_response(spawn, response=""):
    chatty_term_wait(spawn)
    spawn.sendline(response)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Reload  Statements
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

ap_shell_prompt = Statement(pattern=pat.ap_shell_prompt,
                            action=send_response, args={'response': '\r'},
                            loop_continue=True,
                            continue_timer=False)

ap_reload_list = list(reload_statement_list)
ap_reload_list.insert(0,ap_shell_prompt)