__author__ = "dwapstra"

import re

from unicon.eal.dialogs import Statement, Dialog
from unicon.plugins.generic.statements import generic_statements, chatty_term_wait
from unicon.plugins.generic.service_statements import connection_closed

from unicon.utils import to_plaintext
from unicon.core.errors import UniconAuthenticationError

from .patterns import FxosPatterns

patterns = FxosPatterns()


def flag_ssh_session(spawn, context, session):
    context._ssh_session = True
    spawn.log.info('SSH session detected')


def clear_command_line(spawn, context, session):
    """ Clear the command line by sending Ctr-A Ctrl-K """
    CTRL_A = '\x01'
    CTRL_K = '\x0b'
    spawn.sendline("%s%s\r" % (CTRL_A, CTRL_K))


def enable_username_handler(spawn, context, session):
    credentials = context.get('credentials')
    enable_username = to_plaintext(credentials.get('enable', {}).get('username', ''))
    spawn.sendline(enable_username)


# Overriding the generic enable password handler, since the password for ASA can be empty
def enable_password_handler(spawn, context, session):
    if 'password_attempts' not in session:
        session['password_attempts'] = 1
    else:
        session['password_attempts'] += 1
    if session.password_attempts > spawn.settings.PASSWORD_ATTEMPTS:
        raise UniconAuthenticationError('Too many enable password retries')

    credentials = context.get('credentials')
    enable_password = to_plaintext(credentials.get('enable', {}).get('password', ''))
    spawn.sendline(enable_password)


def boot_wait(spawn, timeout=600):
    def count(spawn, context, session):
        m = re.findall(spawn.settings.BOOT_WAIT_PATTERN, spawn.buffer, re.M)
        session['matches'] = session.get('matches', len(m)) + len(m)
        matches = session['matches']
        if matches >= spawn.settings.BOOT_WAIT_PATTERN_COUNT:
            raise ValueError

    wait_dialog = Dialog([Statement(spawn.settings.BOOT_WAIT_PATTERN,
                                    action=count,
                                    loop_continue=True,
                                    continue_timer=True)])
    while True:
        try:
            wait_dialog.process(spawn, timeout=timeout)
        except ValueError:
            break

    # Wait a bit until the terminal is finished logging the interfaces messages
    chatty_term_wait(spawn)


class FxosStatements(object):
    def __init__(self):
        '''
         All FTD Statements
        '''
        self.cssp_stmt = Statement(patterns.cssp_pattern,
                                   action=flag_ssh_session,
                                   args=None,
                                   loop_continue=True,
                                   continue_timer=False)

        self.bell_stmt = Statement(patterns.bell_pattern,
                                   action=clear_command_line,
                                   args=None,
                                   loop_continue=True,
                                   continue_timer=False)

        self.command_not_completed_stmt = Statement(patterns.command_not_completed,
                                                    action=clear_command_line,
                                                    args=None,
                                                    loop_continue=True,
                                                    continue_timer=False)

        self.config_call_home_stmt = Statement(patterns.config_call_home_prompt,
                                               action='sendline(n)',
                                               args=None,
                                               loop_continue=True,
                                               continue_timer=False)

        self.ftd_reboot_confirm_stmt = Statement(patterns.ftd_reboot_confirm,
                                                 action='sendline(yes)',
                                                 args=None,
                                                 loop_continue=True,
                                                 continue_timer=False)

        self.fxos_mgmt_reboot_stmt = Statement(patterns.fxos_mgmt_reboot_confirm,
                                               action='sendline(yes)',
                                               args=None,
                                               loop_continue=True,
                                               continue_timer=False)

        self.enable_username_stmt = Statement(patterns.username,
                                              action=enable_username_handler,
                                              args=None,
                                              loop_continue=True,
                                              continue_timer=False)

        self.enable_password_stmt = Statement(patterns.password,
                                              action=enable_password_handler,
                                              args=None,
                                              loop_continue=True,
                                              continue_timer=False)

        self.boot_interrupt_stmt = Statement(patterns.boot_interrupt,
                                             action='send(\x1b)',
                                             args=None,
                                             loop_continue=True,
                                             continue_timer=False)


fxos_statements = FxosStatements()

default_statement_list = [
    fxos_statements.cssp_stmt,
    fxos_statements.bell_stmt,
    fxos_statements.command_not_completed_stmt,
    generic_statements.more_prompt_stmt
]

reload_statements = [
    fxos_statements.fxos_mgmt_reboot_stmt,
    fxos_statements.ftd_reboot_confirm_stmt,
    Statement(patterns.restarting_system, loop_continue=False),
    Statement(patterns.reboot_requested, loop_continue=False),
    connection_closed
]

boot_to_rommon_statements = [
    fxos_statements.fxos_mgmt_reboot_stmt,
    fxos_statements.ftd_reboot_confirm_stmt,
    fxos_statements.boot_interrupt_stmt
]

login_statements = [
    generic_statements.login_stmt,
    generic_statements.password_stmt,
]
