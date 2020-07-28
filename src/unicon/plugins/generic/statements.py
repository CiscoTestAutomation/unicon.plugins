"""
Module:
    unicon.plugins.generic

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    Module for defining all the Statements and callback required for the
    Current implementation
"""
import re
from time import sleep
from unicon.eal.dialogs import Statement
from unicon.eal.helpers import sendline
from unicon.core.errors import UniconAuthenticationError
from unicon.utils import Utils

from unicon.plugins.generic.patterns import GenericPatterns
from unicon.plugins.utils import (get_current_credential,
    common_cred_username_handler, common_cred_password_handler, )

from unicon.utils import to_plaintext
from unicon.bases.routers.connection import ENABLE_CRED_NAME

pat = GenericPatterns()
utils = Utils()

#############################################################
#  Callbacks
#############################################################

def connection_refused_handler(spawn):
    """ handles connection refused scenarios
    """
    raise Exception('Connection refused to device %s' % (str(spawn),))


def connection_failure_handler(spawn, err):
    raise Exception(err)


def chatty_term_wait(spawn, trim_buffer=False):
    """ Wait a small amount of time for any chatter to cease from the device.
    """
    prev_buf_len = len(spawn.buffer)
    for retry_number in range(
            spawn.settings.ESCAPE_CHAR_CHATTY_TERM_WAIT_RETRIES):

        sleep(spawn.settings.ESCAPE_CHAR_CHATTY_TERM_WAIT)

        spawn.read_update_buffer()

        cur_buf_len = len(spawn.buffer)

        if prev_buf_len == cur_buf_len:
            break
        else:
            prev_buf_len = cur_buf_len
            if trim_buffer:
                spawn.trim_buffer()


def escape_char_callback(spawn):
    """ Wait a small amount of time for terminal chatter to cease before
    attempting to obtain prompt, do not attempt to obtain prompt if login message is seen.
    """

    chatty_term_wait(spawn)

    # Device is already asking for authentication
    if re.search(
        r'.*(User Access Verification|sername:\s*$|assword:\s*$|login:\s*$)',
        spawn.buffer):
        return

    auth_pat = ''
    if spawn.settings.LOGIN_PROMPT:
        auth_pat = spawn.settings.LOGIN_PROMPT
    if spawn.settings.PASSWORD_PROMPT:
        if auth_pat:
            auth_pat += '|' + spawn.settings.PASSWORD_PROMPT
        else:
            auth_pat = spawn.settings.PASSWORD_PROMPT

    if auth_pat and re.search(auth_pat, spawn.buffer):
        return

    # try and get to the first prompt
    # best effort handling of network delays and connection establishing

    # store current know buffer
    known_buffer = len(spawn.buffer.strip())

    for retry_number in range(spawn.settings.ESCAPE_CHAR_PROMPT_WAIT_RETRIES):
        # hit enter
        spawn.sendline()
        spawn.read_update_buffer()

        # incremental sleep logic
        sleep(spawn.settings.ESCAPE_CHAR_PROMPT_WAIT*(retry_number+1))

        # did we get prompt after?
        spawn.read_update_buffer()

        # check buffer
        if known_buffer != len(spawn.buffer.strip()):
            # we got new stuff - assume it's the the prompt, get out
            break

def ssh_continue_connecting(spawn):
    """ handles SSH new key prompt
    """
    sleep(0.1)
    spawn.sendline('yes')


def login_handler(spawn, context, session):
    """ handles login prompt
    """
    credential = get_current_credential(context=context, session=session)
    if credential:
        common_cred_username_handler(
            spawn=spawn, context=context, credential=credential)
    else:
        spawn.sendline(context['username'])
        session['tacacs_login'] = 1


def user_access_verification(session):
    # Enable the tacacs_login flag
    session['tacacs_login'] = 1


def get_enable_credential_password(context):
    """ Get the enable password from the credentials.

    1. If there is a previous credential (the last credential used to respond to
       a password prompt), use its enable_password member if it exists.
    2. Otherwise, if the user specified a list of credentials, pick the final one in the list and
       use its enable_password member if it exists.
    3. Otherwise, if there is a default credential, use its enable_password member if it exists.
    4. Otherwise, use the well known "enable" credential, password member if it exists.
    5. Otherwise, use the default credential "password" member if it exists.
    6. Otherwise, raise error that no enable password could be found.

    """
    credentials = context.get('credentials')
    enable_credential_password = ""
    login_creds = context.get('login_creds', [])
    fallback_cred = context.get('default_cred_name', "")
    if not login_creds:
        login_creds=[fallback_cred]
    if not isinstance (login_creds, list):
        login_creds = [login_creds]

    # Pick the last item in the login_creds list to select the intended
    # credential even if the device does not ask for a password on login
    # and the given credential is not consumed.
    final_credential = login_creds[-1] if login_creds else ""
    if credentials:
        enable_pw_checks = [
            (context.get('previous_credential', ""), 'enable_password'),
            (final_credential, 'enable_password'),
            (fallback_cred, 'enable_password'),
            (ENABLE_CRED_NAME, 'password'),
            (context.get('default_cred_name', ""), 'password'),
        ]
        for cred_name, key in enable_pw_checks:
            if cred_name:
                candidate_enable_pw = credentials.get(cred_name, {}).get(key)
                if candidate_enable_pw:
                    enable_credential_password = candidate_enable_pw
                    break
        else:
            raise UniconAuthenticationError('{}: Could not find an enable credential.'.\
                format(context.get('hostname', "")))
    return to_plaintext(enable_credential_password)


def enable_password_handler(spawn, context, session):
    if 'password_attempts' not in session:
        session['password_attempts'] = 1
    else:
        session['password_attempts'] += 1
    if session.password_attempts > spawn.settings.PASSWORD_ATTEMPTS:
        raise UniconAuthenticationError('Too many enable password retries')

    enable_credential_password = get_enable_credential_password(context=context)
    if enable_credential_password:
        spawn.sendline(enable_credential_password)
    else:
        spawn.sendline(context['enable_password'])


def ssh_tacacs_handler(spawn, context):
    result = False
    start_cmd = spawn.spawn_command
    if re.search(context['username'] + r'@', start_cmd) \
        or re.search(r'-l\s*' + context['username'], start_cmd) \
        or re.search(context['username'] + r'@', spawn.buffer):
        result = True
    return result


def password_handler(spawn, context, session):
    """ handles password prompt
    """
    credential = get_current_credential(context=context, session=session)
    if credential:
        common_cred_password_handler(
            spawn=spawn, context=context, credential=credential,
            session=session)
    else:
        if 'password_attempts' not in session:
            session['password_attempts'] = 1
        else:
            session['password_attempts'] += 1
        if session.password_attempts > spawn.settings.PASSWORD_ATTEMPTS:
            raise UniconAuthenticationError('Too many password retries')

        if context['username'] == spawn.last_sent.rstrip() or \
            ssh_tacacs_handler(spawn, context):
            spawn.sendline(context['tacacs_password'])
        else:
            spawn.sendline(context['line_password'])


def passphrase_handler(spawn, context, session):
    """ Handles SSH passphrase prompt """
    credential = get_current_credential(context=context, session=session)
    try:
        spawn.sendline(to_plaintext(
            context['credentials'][credential]['passphrase']))
    except KeyError:
        raise UniconAuthenticationError("No passphrase found "
                                        "for credential {}.".format(credential))


def bad_password_handler(spawn):
    """ handles bad password prompt
    """
    raise UniconAuthenticationError('Bad Password sent to device %s' % (str(spawn),))


def incorrect_login_handler(spawn, context, session):
    # In nxos device if the first attempt password prompt occur before
    # username prompt, it will get Login incorrect error.
    # Reset the cred_iter to try again
    if 'incorrect_login_attempts' not in session:
        session.pop('cred_iter', None)

    credential = get_current_credential(context=context, session=session)
    if credential and 'incorrect_login_attempts' in session:
        # If credentials have been supplied, there are no login retries.
        # The user must supply appropriate credentials to ensure login
        # does not fail. Skip it for the first attempt
        raise UniconAuthenticationError(
            'Login failure, either wrong username or password')
    else:
        if 'incorrect_login_attempts' not in session:
            session['incorrect_login_attempts'] = 1

        # Let's give a chance for unicon to login with right credentials
        # let's give three attempts
        if session['incorrect_login_attempts'] <=3:
            session['incorrect_login_attempts'] = \
                session['incorrect_login_attempts'] + 1
        else:
            raise UniconAuthenticationError(
                'Login failure, either wrong username or password')


def wait_and_enter(spawn):
    sleep(0.5)  # otherwise newline is sometimes lost?
    spawn.sendline()


def more_prompt_handler(spawn):
    output = utils.remove_backspace(spawn.match.match_output)
    all_more = re.findall(spawn.settings.MORE_REPLACE_PATTERN, output)
    spawn.match.match_output = ''.join(output.rsplit(all_more[-1], 1))
    spawn.send(spawn.settings.MORE_CONTINUE)


def custom_auth_statements(login_pattern=None, password_pattern=None):
    """ Return list of Statements based on login_pattern and password_prompt."""
    stmt_list = []
    if login_pattern:
        login_stmt = Statement(pattern=login_pattern,
                                action=login_handler,
                                args=None,
                                loop_continue=True,
                                continue_timer=False)
        stmt_list.append(login_stmt)
    if password_pattern:
        password_stmt = Statement(pattern=password_pattern,
                                   action=password_handler,
                                   args=None,
                                   loop_continue=True,
                                   continue_timer=False)
        stmt_list.append(password_stmt)
    if stmt_list:
        return stmt_list


#############################################################
#  Generic statements
#############################################################

class GenericStatements():
    """
        Class that defines All the Statements for Generic platform
        implementation
    """

    def __init__(self):
        '''
         All generic Statements
        '''
        self.escape_char_stmt = Statement(pattern=pat.escape_char,
                                          action=escape_char_callback,
                                          args=None,
                                          loop_continue=True,
                                          continue_timer=False)
        self.press_return_stmt = Statement(pattern=pat.press_return,
                                           action=sendline, args=None,
                                           loop_continue=True,
                                           continue_timer=False)
        self.connection_refused_stmt = \
            Statement(pattern=pat.connection_refused,
                      action=connection_refused_handler,
                      args=None,
                      loop_continue=False,
                      continue_timer=False)

        self.bad_password_stmt = Statement(pattern=pat.bad_passwords,
                                           action=bad_password_handler,
                                           args=None,
                                           loop_continue=False,
                                           continue_timer=False)

        self.login_incorrect = Statement(pattern=pat.login_incorrect,
                                           action=incorrect_login_handler,
                                           args=None,
                                           loop_continue=True,
                                           continue_timer=False)

        self.disconnect_error_stmt = Statement(pattern=pat.disconnect_message,
                                               action=connection_failure_handler,
                                               args={
                                               'err': 'received disconnect from router'},
                                               loop_continue=False,
                                               continue_timer=False)
        self.login_stmt = Statement(pattern=pat.username,
                                    action=login_handler,
                                    args=None,
                                    loop_continue=True,
                                    continue_timer=False)
        self.useraccess_stmt = Statement(pattern=pat.useracess,
                                         action=user_access_verification,
                                         args=None,
                                         loop_continue=True,
                                         continue_timer=False)
        self.password_stmt = Statement(pattern=pat.password,
                                       action=password_handler,
                                       args=None,
                                       loop_continue=True,
                                       continue_timer=False)
        self.enable_password_stmt = Statement(pattern=pat.password,
                                       action=enable_password_handler,
                                       args=None,
                                       loop_continue=True,
                                       continue_timer=False)
        self.password_ok_stmt = Statement(pattern=pat.password_ok,
                                             action=sendline,
                                             args=None,
                                             loop_continue=True,
                                             continue_timer=False)
        self.more_prompt_stmt = Statement(pattern=pat.more_prompt,
                                          action=more_prompt_handler,
                                          args=None,
                                          loop_continue=True,
                                          continue_timer=False)
        self.confirm_prompt_stmt = Statement(pattern=pat.confirm_prompt,
                                             action=sendline,
                                             args=None,
                                             loop_continue=True,
                                             continue_timer=False)
        self.confirm_prompt_y_n_stmt = Statement(pattern=pat.confirm_prompt_y_n,
                                                 action='sendline(y)',
                                                 args=None,
                                                 loop_continue=True,
                                                 continue_timer=False)
        self.yes_no_stmt = Statement(pattern=pat.yes_no_prompt,
                                     action=sendline,
                                     args={'command': 'y'},
                                     loop_continue=True,
                                     continue_timer=False)

        self.continue_connect_stmt = Statement(pattern=pat.continue_connect,
                                action=ssh_continue_connecting,
                                args=None,
                                loop_continue=True,
                                continue_timer=False)

        self.hit_enter_stmt = Statement(pattern=pat.hit_enter,
                                action=wait_and_enter,
                                args=None,
                                loop_continue=True,
                                continue_timer=False)

        self.press_ctrlx_stmt = Statement(pattern=pat.press_ctrlx,
                                              action=wait_and_enter,
                                              args=None,
                                              loop_continue=True,
                                              continue_timer=False)

        self.init_conf_stmt = Statement(pattern=pat.setup_dialog,
                                        action='sendline(no)',
                                        args=None,
                                        loop_continue=True,
                                        continue_timer=False)

        self.mgmt_setup_stmt = Statement(pattern=pat.enter_basic_mgmt_setup,
                                        action='send(\x03)', # Ctrl-C
                                        args=None,
                                        loop_continue=True,
                                        continue_timer=False)

        self.clear_kerberos_no_realm = Statement(pattern=pat.kerberos_no_realm,
                                                  action=sendline,
                                                  args=None,
                                                  loop_continue=True,
                                                  continue_timer=False)

        self.connected_stmt = Statement(pattern=pat.connected,
                                        action=sendline,
                                        args=None,
                                        loop_continue=True,
                                        continue_timer=False)

        self.passphrase_stmt = Statement(pattern=pat.passphrase_prompt,
                                         action=passphrase_handler,
                                         args=None,
                                         loop_continue=True,
                                         continue_timer=False)

#############################################################
#  Statement lists
#############################################################

generic_statements = GenericStatements()

#############################################################
# Initial connection Statements
#############################################################

pre_connection_statement_list = [generic_statements.escape_char_stmt,
                                 generic_statements.press_return_stmt,
                                 generic_statements.continue_connect_stmt,
                                 generic_statements.connection_refused_stmt,
                                 generic_statements.disconnect_error_stmt,
                                 generic_statements.hit_enter_stmt,
                                 generic_statements.press_ctrlx_stmt,
                                 generic_statements.connected_stmt,
                                 ]

#############################################################
# Authentication Statements
#############################################################

authentication_statement_list = [generic_statements.bad_password_stmt,
                                 generic_statements.login_incorrect,
                                 generic_statements.login_stmt,
                                 generic_statements.useraccess_stmt,
                                 generic_statements.password_stmt,
                                 generic_statements.clear_kerberos_no_realm,
                                 generic_statements.password_ok_stmt,
                                 generic_statements.passphrase_stmt
                                 ]

#############################################################
# Setup Statements
#############################################################

initial_statement_list = [generic_statements.init_conf_stmt,
                          generic_statements.mgmt_setup_stmt
                         ]

connection_statement_list = authentication_statement_list + initial_statement_list + pre_connection_statement_list


############################################################
# Default pattern Statement
#############################################################

default_statement_list = [generic_statements.more_prompt_stmt]
