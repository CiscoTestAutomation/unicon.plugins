'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''
from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.aos.patterns import aosPatterns
from unicon.plugins.generic.statements import pre_connection_statement_list
from unicon.plugins.generic.statements import password_handler
from unicon.plugins.generic.statements import login_handler
from unicon.plugins.generic.statements import enable_password_handler
from unicon.eal.helpers import sendline
import time

patterns = aosPatterns()

def escape_char_handler(spawn):
    """ handles telnet login messages
    """
    # Wait a small amount of time for any chatter to cease from the
    # device before attempting to call sendline.

def run_level():
    sleep(2)


class aosStatements(object):
    def __init__(self):


# This is the statements to login to AOS.
        self.start_stmt = Statement(pattern=patterns.start,
                                    action=run_level,
                                    args=None,
                                    loop_continue=True,
                                    continue_timer=True,
                                    trim_buffer=False,
                                    debug_statement=True)
        self.login_stmt = Statement(pattern=patterns.login_prompt,
                                    action=login_handler,
                                    args=None,
                                    loop_continue=True,
                                    continue_timer=True,
                                    trim_buffer=False,
                                    debug_statement=True)
        self.password_stmt = Statement(pattern=patterns.password,
                                       action=password_handler,
                                       args=None,
                                       loop_continue=True,
                                       continue_timer=True,
                                       trim_buffer=False,
                                       debug_statement=True,
                                       matched_retries=3,
                                       matched_retry_sleep=1)
        self.ssh_key_check = Statement(pattern=patterns.proxy,
                                    action='sendline(yes)',
                                    args=None,
                                    loop_continue=True,
                                    continue_timer=True,
                                    trim_buffer=False,
                                    debug_statement=True,
                                    matched_retries=3,
                                    matched_retry_sleep=1)
        self.press_any_key_stmt = Statement(pattern=patterns.press_any_key,
                                            action='sendline()',
                                            args=None,
                                            loop_continue=True,
                                            continue_timer=True,
                                            trim_buffer=False,
                                            debug_statement=True,
                                            matched_retries=3,
                                            matched_retry_sleep=1)       

#############################################################
#  Statement lists
#############################################################

aos_statements = aosStatements()

#############################################################
# Authentication Statements
#############################################################

aosAuthentication_statement_list = [aos_statements.start_stmt,
                                 aos_statements.login_stmt,
                                 aos_statements.password_stmt,
                                 aos_statements.press_any_key_stmt,
                                 aos_statements.ssh_key_check]

aosConnection_statement_list = aosAuthentication_statement_list