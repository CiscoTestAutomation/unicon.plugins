"""
Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)
"""

import re
import time

from unicon.eal.dialogs import Dialog, Statement
from unicon.bases.routers.connection_provider import BaseStackRpConnectionProvider

from unicon.plugins.generic.statements import (connection_statement_list,
                                               custom_auth_statements,
                                               GenericStatements)

statements = GenericStatements()


##show switch
#   *1       Active   74e2.e72d.8180     1      V07     Ready
#    3       Standby  74e2.e72d.9080     1      V07     Ready
SHOW_SWITCH_ROW_RE = re.compile(
    r'^\s*(?P<local>\*)?\s*(?P<sw_num>\d+)\s+'
    r'(?P<role>Active|Standby|Member)\b', re.IGNORECASE | re.MULTILINE)

# Only one session may hold the standby console TTY; a stale attach elsewhere
# makes the device answer 'ioucon:TTY open (remote): Address already in use'.
CONSOLE_BUSY_PATTERN = r'.*(Address already in use|TTY open.*in use).*'

# The attached console stays silent after this banner until it gets a newline.
CONSOLE_BANNER_PATTERN = r'.*Enter Control-C to exit.*'


def _console_busy_handler(spawn, context):
    """Mark the attach as refused so we can fail fast instead of timing out."""
    context['_standby_console_busy'] = True


def _console_banner_handler(spawn, context):
    """Poke the attached console so it prints its prompt."""
    spawn.sendline()


def _console_rejected_handler(spawn, context):
    """Mark the attach as not taken, so we stop instead of waiting it out."""
    context['_standby_console_rejected'] = True


class StackRpConnectionProvider(BaseStackRpConnectionProvider):
    """ Implements Stack Connection Provider,
        This class overrides the base class with the
        additional dialogs and steps required for
        connecting to stack device
    """
    def __init__(self, *args, **kwargs):

        """ Initializes the base connection provider
        """
        super().__init__(*args, **kwargs)

    def get_connection_dialog(self):
        """ creates and returns a Dialog to handle all device prompts
            appearing during initial connection to the device.
            See generic/statements.py for connnection statement lists
        """
        con = self.connection
        custom_auth_stmt = custom_auth_statements(
                             self.connection.settings.LOGIN_PROMPT,
                             self.connection.settings.PASSWORD_PROMPT)
        return con.connect_reply + \
                    Dialog(custom_auth_stmt + connection_statement_list
                        if custom_auth_stmt else connection_statement_list)

    # ------------------------------------------------------------------
    # Standby console attach
    # ------------------------------------------------------------------
    def _get_local_switch(self, con, timeout=30):
        """Return (switch number, role) from the '*' row of 'show switch'.

        The '*' row is console-local, unlike 'show switch <N>'.
        """
        try:
            output = con.execute('show switch', timeout=timeout)
        except Exception as exc:
            con.log.debug('Could not read stack roles: %s' % exc)
            return None, None

        for match in SHOW_SWITCH_ROW_RE.finditer(output or ''):
            if match.group('local'):
                return match.group('sw_num'), match.group('role').capitalize()
        return None, None

    def _attach_standby_console(self, con):
        """Descend from an active-RP session into the standby RP console.

        Runs 'request platform software console attach switch standby <plane>',
        answers the login it raises, and leaves the handle in enable state.
        """
        settings = self.connection.settings
        plane = getattr(settings, 'STACK_STANDBY_CONSOLE_PLANE', 'R0')
        timeout = getattr(settings,
                          'STACK_STANDBY_CONSOLE_ATTACH_TIMEOUT', 120)

        command = ('request platform software console attach switch standby %s'
                   % plane)
        con.log.info('+++ attaching to standby RP console +++')

        # Make sure we are at enable on the active before descending.
        con.state_machine.go_to('enable',
                                con.spawn,
                                context=con.context,
                                prompt_recovery=self.prompt_recovery,
                                timeout=con.connection_timeout)

        # The attach banner is followed by a fresh 'User Access Verification'
        # login. Reuse the standard auth statements so testbed credentials are
        # applied, and tolerate the platform's informational/warning lines.
        custom_auth_stmt = custom_auth_statements(settings.LOGIN_PROMPT,
                                                  settings.PASSWORD_PROMPT)
        busy_stmt = Statement(pattern=CONSOLE_BUSY_PATTERN,
                              action=_console_busy_handler,
                              args=None,
                              loop_continue=False,
                              continue_timer=False)
        banner_stmt = Statement(pattern=CONSOLE_BANNER_PATTERN,
                                action=_console_banner_handler,
                                args=None,
                                loop_continue=True,
                                continue_timer=True)

        # Terminate only on the standby prompt ('<host>-stby>' or '-stby#').
        # The pattern requires '-stby' so it cannot match the active's prompt
        # if the attach fails or is rejected.
        hostname = con.context.get('hostname') or con.hostname
        prompt_stmt = Statement(pattern=r'^.*%s[\w\-]*-stby[>#]\s?$'
                                        % re.escape(hostname),
                                action=None,
                                args=None,
                                loop_continue=False,
                                continue_timer=False)

        # Landing back on the active's prompt means the attach was rejected or
        # is unsupported; stop rather than poking until the timeout expires.
        rejected_stmt = Statement(pattern=r'^.*%s(?<!-stby)[>#]\s?$'
                                          % re.escape(hostname),
                                  action=_console_rejected_handler,
                                  args=None,
                                  loop_continue=False,
                                  continue_timer=False)

        dialog = Dialog((custom_auth_stmt or []) + [
            busy_stmt,
            banner_stmt,
            statements.login_stmt,
            statements.password_stmt,
            statements.enable_password_stmt,
            statements.bad_password_stmt,
            statements.syslog_stripper_stmt,
            statements.syslog_msg_stmt,
            prompt_stmt,
            rejected_stmt,
        ])

        con.context.pop('_standby_console_busy', None)
        con.context.pop('_standby_console_rejected', None)
        con.spawn.buffer = ''
        con.sendline(command)

        # The attached console prints nothing until it is poked with a newline,
        # and a poke sent before it is ready is swallowed, so poke repeatedly
        # with a short timeout rather than waiting out one long one. Prompt
        # recovery is off here because its Ctrl-C would exit the very console
        # being attached to.
        poll = getattr(settings, 'STACK_STANDBY_CONSOLE_POLL_INTERVAL', 20)
        deadline = time.time() + timeout
        while True:
            try:
                dialog.process(con.spawn,
                               context=con.context,
                               prompt_recovery=False,
                               timeout=min(poll,
                                           max(1, deadline - time.time())))
                break
            except Exception as exc:
                if con.context.get('_standby_console_busy') or \
                        con.context.get('_standby_console_rejected'):
                    break
                if time.time() >= deadline:
                    con.log.warning(
                        'Standby console attach dialog ended: %s' % exc)
                    break
                con.spawn.sendline()

        if con.context.pop('_standby_console_rejected', False):
            con.log.error(
                'Standby console attach was not accepted; the session is still '
                'on the active RP. device.standby and swap_roles() will not '
                'reach the standby.')
            con.state_machine.detect_state(con.spawn, context=con.context)
            return

        if con.context.pop('_standby_console_busy', False):
            con.log.error(
                'Standby console is already in use by another session '
                '("Address already in use"). Only one session may attach to '
                'the standby RP console at a time. Close any manual telnet '
                'session that ran "request platform software console attach" '
                '(send Ctrl-C to exit it), or clear the terminal-server line, '
                'then reconnect.')
            # Leave the handle on the active in a known state.
            con.state_machine.detect_state(con.spawn, context=con.context)
            return

        # The attached session starts in disable mode ('<host>-stby>'). The
        # iosxe disable/enable prompt patterns already tolerate the '-stby'
        # suffix, so a normal state detection + go_to('enable') completes it.
        con.state_machine.detect_state(con.spawn, context=con.context)
        con.state_machine.go_to('enable',
                                con.spawn,
                                context=con.context,
                                prompt_recovery=self.prompt_recovery,
                                timeout=con.connection_timeout)
        # Remember so disconnect() can release the console for the next run.
        con._standby_console_attached = True

    def _release_stale_console_attach(self, con):
        """Exit a console attach left behind by an earlier run.

        The attach lives on the terminal-server line, not the telnet session,
        so it survives a disconnect and reconnecting lands back in '-stby#'.
        Left in place, the probe below reads STANDBY and skips the attach --
        a false green. Ctrl-C is harmless at a normal prompt.
        """
        try:
            con.spawn.send('\x03')
            time.sleep(2)
            con.spawn.sendline()
            time.sleep(1)
            con.spawn.buffer = ''
            con.state_machine.detect_state(con.spawn, context=con.context)
        except Exception as exc:
            con.log.debug('Stale console attach release skipped: %s' % exc)
        finally:
            con._standby_console_attached = False

    def _detach_standby_console(self, con):
        """Ctrl-C out of the standby console so the next connect can attach.

        Only one session may hold the standby TTY.
        """
        try:
            con.log.info('+++ detaching from standby RP console +++')
            con.spawn.send('\x03')
            time.sleep(2)
            con.spawn.sendline()
            time.sleep(1)
            con.spawn.buffer = ''
        except Exception as exc:
            con.log.warning('Failed to detach standby console: %s' % exc)
        finally:
            con._standby_console_attached = False

    def disconnect(self):
        """Release the standby console (if we attached it) before disconnecting."""
        for subcon in getattr(self.connection, 'subconnections', []) or []:
            if getattr(subcon, '_standby_console_attached', False):
                self._detach_standby_console(subcon)
        super().disconnect()

    def init_standby(self):
        """Initialise the standby handle, attaching its console if needed.

        On a stack every member console connects to the active, so the
        designated standby handle is a second session on the active and
        device.standby / target='standby' / swap_roles() silently use it.
        """
        con = self.connection
        sby_con = con.standby
        settings = con.settings

        if getattr(settings, 'STACK_STANDBY_CONSOLE_ATTACH', False):
            standby_alias = self._find_standby_console()

            if standby_alias is not None:
                con.log.info(
                    "Connection '%s' is on the standby RP; no console attach "
                    "needed." % standby_alias)
                if standby_alias != getattr(sby_con, 'alias', None):
                    con.log.warning(
                        "Standby console is '%s' but the standby handle is "
                        "'%s'. device.standby will not reach the standby RP."
                        % (standby_alias, getattr(sby_con, 'alias', None)))
            else:
                sby_con.log.info(
                    'No console reaches the standby RP; attaching to the '
                    'standby console.')
                self._attach_standby_console(sby_con)

                # The first read straight after the attach can come back empty
                # because the session has just switched prompts; retry once.
                sw_num, role = self._get_local_switch(sby_con)
                if role is None:
                    sw_num, role = self._get_local_switch(sby_con)

                if role == 'Standby':
                    sby_con.log.info(
                        'Standby console attach successful (switch %s).'
                        % sw_num)
                else:
                    sby_con.log.warning(
                        'Standby console attach did not reach the standby RP '
                        '(role = %s).' % role)

        super().init_standby()

    def set_init_commands(self):
        """Drop init commands the attached standby console cannot sustain.

        The standby RP console is rate limited: 'show version' stalls part way
        and times out the connect. The active handle keeps the full set.
        """
        super().set_init_commands()

        sby_con = getattr(self.connection, 'standby', None)
        if not getattr(sby_con, '_standby_console_attached', False):
            return

        skip = getattr(self.connection.settings,
                       'STACK_STANDBY_CONSOLE_SKIP_INIT_COMMANDS', [])
        if skip:
            self.init_exec_commands = [cmd for cmd in self.init_exec_commands
                                       if cmd not in skip]

    def _find_standby_console(self):
        """Return the alias of a console on the standby RP, else None.

        Probes every console, not just the designated standby handle: the
        designation is positional and the standby can be any switch. Stale
        attaches are cleared first so each console reports its own identity.
        """
        con = self.connection
        subcons = list(getattr(con, '_subconnections', {}).items()) or \
            [(getattr(con.standby, 'alias', 'standby'), con.standby)]

        for alias, subcon in subcons:
            self._release_stale_console_attach(subcon)

            sw_num, role = self._get_local_switch(subcon)
            subcon.log.info("Connection '%s' is on switch %s (%s)"
                            % (alias, sw_num, role))
            if role == 'Standby':
                return alias
        return None
