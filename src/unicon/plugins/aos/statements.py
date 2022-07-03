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
from unicon.plugins.utils import (
    get_current_credential,
    common_cred_username_handler,
    common_cred_password_handler,
)
import getpass
import logging
#Logging disable disables logging in the script. In order to turn on logging, comment out logging disable.
#logging.disable(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
patterns = aosPatterns()

def escape_char_handler(spawn):
    """ handles telnet login messages
    """
    logging.debug('***Statements escape char handler function called(%s)***')
    # Wait a small amount of time for any chatter to cease from the
    # device before attempting to call sendline.
    time.sleep(.2)

def run_level(spawn):
    logging.debug('***Statements run level function called(%s)***')
    time.sleep(1)
#    secret = getpass.getpass("Enter secret:")



def ssh_continue_connecting(spawn):
    """ handles SSH new key prompt
    """
    logging.debug('***Statements ssh continue connecting function called(%s)***')
    time.sleep(0.1)
    print("I saw the ssh key configuration")
    spawn.sendline('yes')


def wait_and_enter(spawn):
    logging.debug('***Statements wait and enter function called(%s)***')
    # wait for 0.5 second and read the buffer
    # this avoids issues where the 'sendline'
    # is somehow lost
    
    spawn.sendline()

def send_password(spawn):
    logging.debug('***Statements password handler called(%s)***')
    secret = getpass.getpass("Enter secret:")
    spawn.send(secret + "\r")

'''
Example:

    dialog = Dialog([
        Statement(pattern=r"^username:$",
                  action=lambda spawn: spawn.sendline("admin"),
                  args=None,
                  loop_continue=True,
                  continue_timer=False ),
        Statement(pattern=r"^password:$",
                  action=lambda spawn: spawn.sendline("admin"),
                  args=None,
                  loop_continue=True,
                  continue_timer=False ),
        Statement(pattern=r"^host-prompt#$",
                  action=None,
                  args=None,
                  loop_continue=False,
                  continue_timer=False ),
    ])

    It is also possible to construct a dialog instance by supplying list of
    statement arguments.

    dialog = Dialog([
        [r"^username$", lambda spawn: spawn.sendline("admin"), None, True, False],
        [r"^password:$", lambda spawn: spawn.sendline("admin"), None, True, False],
        [r"^hostname#$", None, None, False, False]
    ])
'''

class aosStatements(object):
    
    def __init__(self):
        logging.debug('***Statements aosStatements class loaded(%s)***')
# This is the statements to login to AOS.
        self.start_stmt = Statement(pattern=patterns.start,
                                    action=run_level,
                                    args=None,
                                    loop_continue=True,
                                    continue_timer=True,
                                    trim_buffer=True,
                                    debug_statement=True)
        self.login_stmt = Statement(pattern=patterns.login_prompt,
                                    action=login_handler,
                                    args=None,
                                    loop_continue=True,
                                    continue_timer=True,
                                    trim_buffer=True,
                                    debug_statement=True)
        self.password_stmt = Statement(pattern=patterns.password_prompt,
                                       action=send_password,
                                       args=None,
                                       loop_continue=True,
                                       continue_timer=True,
                                       trim_buffer=True,
                                       debug_statement=True)
        self.ssh_key_check = Statement(pattern=patterns.proxy,
                                    action=ssh_continue_connecting,
                                    args=None,
                                    loop_continue=True,
                                    continue_timer=True,
                                    trim_buffer=True,
                                    debug_statement=True)
        self.press_any_key_stmt = Statement(pattern=patterns.press_any_key,
                                            action=wait_and_enter,
                                            args=None,
                                            loop_continue=True,
                                            continue_timer=False,
                                            trim_buffer=True,
                                            debug_statement=True)       

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
