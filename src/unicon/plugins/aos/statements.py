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

patterns = aosPatterns()

def escape_char_handler(spawn):
    """ handles telnet login messages
    """
    # Wait a small amount of time for any chatter to cease from the
    # device before attempting to call sendline.

    prev_buf_len = len(spawn.buffer)
    for retry_number in range(
            settings.ESCAPE_CHAR_CALLBACK_PAUSE_CHECK_RETRIES):
        time.sleep(settings.ESCAPE_CHAR_CALLBACK_PAUSE_SEC)
        spawn.read_update_buffer()
        cur_buf_len = len(spawn.buffer)
        if prev_buf_len == cur_buf_len:
            break
        else:
            prev_buf_len = cur_buf_len

    spawn.sendline()

class aosStatements(object):
    def __init__(self):

# This is the statements to login to AOS.
        self.login_stmt = Statement(pattern=patterns.login_prompt,
                                action=password_handler,
                                args=None,
                                loop_continue=True,
                                continue_timer=True,
                                trim_buffer=True)

        self.password_stmt = Statement(pattern=patterns.password,
                                action=password_handler,
                                args=None,
                                loop_continue=True,
                                continue_timer=True,
                                trim_buffer=True)
        self.proxy_stmt = Statement(pattern=patterns.proxy,
                                    action='sendline(This is where I am failing proxy)',
                                    args=None,
                                    loop_continue=True,
                                    continue_timer=False,
                                    trim_buffer=True)
        self.shell_stmt = Statement(pattern=patterns.shell_prompt,
                                    action='sendline(This is where I am failing shell)',
                                    args=None,
                                    loop_continue=False,
                                    continue_timer=False,
                                    trim_buffer=True)
        escape_char_stmt = Statement(pattern=patterns.escape_char,
                             action=escape_char_handler,
                             args=None,
                             loop_continue=True,
                             continue_timer=False)
        press_return_stmt = Statement(pattern=patterns.press_return,
                              action=sendline, 
                              args=None,
                              loop_continue=True,
                              continue_timer=False)

#############################################################
#  Statement lists
#############################################################

aos_statements = aosStatements()

#############################################################
# Authentication Statements
#############################################################

aosAuthentication_statement_list = [aos_statements.login_stmt,
                                 aos_statements.password_stmt,
                                 aos_statements.shell_stmt,
                                 aos_statements.proxy_stmt]

aosConnection_statement_list = aosAuthentication_statement_list