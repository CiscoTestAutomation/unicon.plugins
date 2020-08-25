__author__ = "dwapstra"

import io
import re
import logging
import collections

from unicon.core.errors import SubCommandFailure, StateMachineError
from unicon.bases.routers.services import BaseService
from unicon.eal.dialogs import Dialog, Statement
from unicon.logs import UniconStreamHandler

from unicon.plugins.generic.service_implementation import Execute as GenericExecute
from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.generic import GenericUtils
from unicon.plugins.utils import slugify
from unicon.core.errors import TimeoutError

from .patterns import StarosPatterns


utils = GenericUtils()
pat = StarosPatterns()


class Command(BaseService):
    """ Service to execute a single command on the ConfD CLI.
    This service is used by the Configure and Execute services
    to execute a single command. Command output is checked for errors
    as part of the services implementation in bases.routers.services.

    Arguments:
        command: command string
        reply: Addition Dialogs for interactive config commands.
        timeout : Timeout value in sec, Default Value is 60 sec

    Returns:
        Command output string
        raise SubCommandFailure on failure
        raise StateMachineError if CLI state is not supported

    Example:
        .. code-block:: python

              output = device.command('show services')

    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.timeout_pattern = ['Timeout occurred', ]
        self.result = None
        self.timeout = connection.settings.EXEC_TIMEOUT

    def log_service_call(self):
        pass

    def pre_service(self, *args, **kwargs):
        pass

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self, command,
                     reply=Dialog([]),
                     timeout=None,
                     error_pattern=None,
                     *args, **kwargs):

        con = self.connection

        timeout = timeout or self.timeout
        if error_pattern is None:
            self.error_pattern = con.settings.ERROR_PATTERN
        else:
            self.error_pattern = error_pattern

        if not isinstance(command, str):
            raise SubCommandFailure('Command is not a string: %s' % type(command))

        sm = self.get_sm()

        con.log.info("+++ command '%s' +++" % command)
        timeout = timeout or con.settings.EXEC_TIMEOUT
        if not isinstance(reply, Dialog):
            raise SubCommandFailure(
                "dialog passed via 'reply' must be an instance of Dialog")

        dialog = Dialog()
        if reply:
            dialog += reply
        for state in sm.states:
            dialog.append(Statement(pattern=state.pattern))
        # dialog.append(statements.more_prompt_stmt)

        con.sendline(command)
        try:
            self.result = dialog.process(con.spawn, timeout=timeout, context=self.context)
        except Exception as err:
            raise SubCommandFailure("Command execution failed", err)

        if self.result:
            self.result = self.result.match_output

        sm.detect_state(con.spawn)
        self.end_state = sm.current_state


class Configure(BaseService):
    """ Service to configure with list of `commands`.

    Configure without any commands will take device to config mode and back to exec mode.
    'command' should be a list or a string.
      Strings can have multiple lines, each line will be executed as a separate command.
      The 'commit' command will be added automatically if not provided.
    'reply' option can be passed for the interactive config command.

    Arguments:
        command: list or string with config command(s)
        reply: Addition Dialogs for interactive config commands.
        timeout : Timeout value in sec, Default Value is 30 sec

    Returns:
        True on Success
        raise SubCommandFailure on failure
        raise StateMachineError if CLI state is not supported

    Example:
        .. code-block:: python

              output = device.configure()
              output = device.configure('services sw-init-l3vpn foo \
               endpoint PE1 pe-interface 0/0/0/1 \
               pe-address 1.1.1.2 \
               ce CE1 ce-interface 0/1 ce-address 1.1.1.1'
              cmds = ["no services sw-init-l3vpn foo", "no services sw-init-l3vpn bar"]
              output = device.configure(cmds, timeout=120)

    """
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'config'
        self.end_state = 'enable'
        self.timeout = connection.settings.CONFIG_TIMEOUT

    def call_service(self, command=[],
                     reply=Dialog([]),
                     timeout=None,
                     error_pattern=None,
                     *args, **kwargs):

        # Get current state of the state machine and determine end state
        sm = self.get_sm()
        con = self.connection

        spawn = self.get_spawn()
        sm.go_to(self.start_state, spawn, context=self.context)

        timeout = timeout or self.timeout
        if isinstance(command, str):
            command = command.splitlines()
        self.command_list_is_empty = False
        if not isinstance(reply, Dialog):
            raise SubCommandFailure(
                "dialog passed via 'reply' must be an instance of Dialog")

        # No command passed, just move to config mode
        if len(command) == 0:
            self.result = None
            self.command_list_is_empty = True
            return

        command_output = {}
        # if commands is a list
        if not isinstance(command, collections.abc.Sequence):
            raise SubCommandFailure('Invalid command passed %s' % repr(command))

        try:
            for cmd in command:
                self.result = con.command(cmd,
                    reply=reply,
                    error_pattern=error_pattern,
                    timeout=timeout)
                if self.result:
                    output = utils.truncate_trailing_prompt(
                                sm.get_state(sm.current_state),
                                self.result,
                                self.connection.hostname)
                    output = output.replace(cmd, "", 1)
                    output = re.sub(r"^\r\n", "", output, 1)
                    command_output[cmd] = output.rstrip()
        except SubCommandFailure:
            # Go to exec state after command failure,
            # do not commit changes (handled by state transition)
            sm.go_to(self.end_state, spawn, context=self.context)
            raise

        if len(command_output) == 1:
            self.result = list(command_output.values())[0]
        else:
            self.result = command_output


class Monitor(GenericExecute):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.service_name = 'monitor'
        self.start_state = 'any'
        self.end_state = 'any'
        self.connection.settings.EXEC_ALLOW_STATE_CHANGE = True
        self.monitor_state = {}
        self.log_buffer = io.StringIO()
        lb = UniconStreamHandler(self.log_buffer)
        lb.setFormatter(logging.Formatter(fmt='[%(asctime)s] %(message)s'))
        self.connection.log.addHandler(lb)
        self.radius_tries = 83

    @property
    def running(self):
        return self.connection.state_machine.current_state == 'monitor'

    def call_service(self, command, *args, **kwargs):
        conn = self.connection
        sm = conn.state_machine
        if not isinstance(command, str):
            raise ValueError('command must be a string')
        command = command.strip()

        if command:
            sm.go_to('enable', conn.spawn)
            if not re.match('^mon', command):
                command = 'monitor ' + command

            # Clear log buffer
            self.log_buffer.seek(0)
            self.log_buffer.truncate()

            super().call_service(command, *args, **kwargs)
            monitor_output = self.result

            date_string = monitor_output.splitlines()[0]
            m = re.match(pat.monitor_date_string, date_string)
            if m:
                date_string = m.group(0)
                self.monitor_state['date'] = date_string

            m = re.findall(pat.monitor_command_pattern, monitor_output)
            if m:
                for x in m:
                    k = slugify(x[1] + x[2])
                    v = slugify(x[3])
                    self.connection.log.debug('Updating {k} to {v}'.format(k=k, v=v))
                    self.monitor_state.update({k: {'state': v, 'id': x[0]}})

        if len(kwargs):
            self._update_monitor_options(**kwargs)

    def _update_monitor_options(self, **kwargs):
        conn = self.connection
        for kw in kwargs:
            if kw in self.monitor_state:
                target_state = kwargs.get(kw)
                conn.log.debug('{kw} target state {target_state}'.format(
                                kw=kw, target_state=target_state))

                if kw == 'verbosity_level':
                    self._update_verbosity(target_state)
                elif kw == 'app_specific_diameter':
                    self._update_app_specific_diameter(target_state)
                elif kw == 'limit_context':
                    self._update_state(kw, target_state, pat.limit_context_state_update, 3)
                elif kw == 'radius_dict':
                    self._update_dict_state(kw, target_state, pat.radius_dict_update, 83)
                elif kw == 'gtpp_dict':
                    self._update_dict_state(kw, target_state, pat.gtpp_dict_update, 60)
                else:
                    self._update_state(kw, target_state, pat.monitor_state_update, 1)

    def _update_verbosity(self, target_state):
        conn = self.connection
        target_state = int(target_state)
        level = int(self.monitor_state['verbosity_level']['state'])
        if level < target_state:
            while level < target_state:
                conn.send('+')
                try:
                    m = conn.expect(pat.monitor_state_update)
                    level = int(m.last_match.group(1).strip())
                except Exception:
                    raise SubCommandFailure('Could not change verbosity')
        elif level > target_state:
            while level > target_state:
                conn.send('-')
                try:
                    m = conn.expect(pat.monitor_state_update)
                    level = int(m.last_match.group(1).strip())
                except Exception:
                    raise SubCommandFailure('Could not change verbosity')
        self.monitor_state['verbosity_level']['state'] = level

    def _update_app_specific_diameter_status(self, monitor_output):
        m = re.findall(pat.monitor_app_specific_diameter, monitor_output)
        if m:
            for x in m:
                k = slugify(x[1])
                v = slugify(x[2])
                self.connection.log.debug('Updating {k} to {v}'.format(k=k, v=v))
                self.monitor_state.update({k: {'state': v, 'id': x[0]}})

    def _update_app_specific_diameter(self, target_state):
        if not isinstance(target_state, dict):
            raise ValueError('Target state should be a dictionary')
        conn = self.connection
        conn.send('75')
        monitor_output = conn.expect(pat.monitor_sub_prompt)
        self._update_app_specific_diameter_status(monitor_output.match_output)
        for kw, target_sub_state in target_state.items():
            current_state = self.monitor_state[kw].get('state')
            if current_state != target_sub_state:
                cmd = self.monitor_state[kw]['id']
                conn.send(cmd)
                monitor_output = conn.expect(pat.monitor_sub_prompt)
                self._update_app_specific_diameter_status(monitor_output.match_output)
                current_state = self.monitor_state[kw].get('state')
                if current_state != target_sub_state:
                    raise SubCommandFailure('Could not change {kw} to state {target_sub_state}'
                                            .format(kw=kw, target_sub_state=target_sub_state))
        conn.send('b')
        conn.expect(pat.monitor_main_prompt)

    def _update_dict_state(self, kw, target_state, update_pattern, max_tries):
        conn = self.connection
        target_state = slugify(target_state)
        current_state = self.monitor_state[kw].get('state')
        tries = 0
        cmd = self.monitor_state[kw]['id']
        while current_state != target_state:
            tries += 1
            if tries > max_tries:
                raise SubCommandFailure('Could not change {kw} to state {target_state}'
                                        .format(kw=kw, target_state=target_state))
            conn.send(cmd)
            m = conn.expect(update_pattern)
            if m:
                current_state = slugify(m.last_match.group(1).strip())
        self.monitor_state[kw]['state'] = current_state

    def _update_state(self, kw, target_state, update_pattern, update_index):
        conn = self.connection
        target_state = slugify(target_state)
        current_state = self.monitor_state[kw].get('state')
        if current_state != target_state:
            cmd = self.monitor_state[kw]['id']
            conn.send(cmd)
            m = conn.expect(update_pattern)
            if m:
                current_state = slugify(m.last_match.group(update_index).strip())
                if current_state != target_state:
                    raise SubCommandFailure('Could not change {kw} to state {target_state}'
                                            .format(kw=kw, target_state=target_state))
                self.monitor_state[kw]['state'] = current_state

    def get_buffer(self, truncate=False):
        """
        Return log buffer contents and clear log buffer if truncate is true
        """
        self.log_buffer.seek(0)
        output = self.log_buffer.read()
        if truncate:
            self.log_buffer.seek(0)
            self.log_buffer.truncate()
        return output

    def tail(self, timeout, pattern=None, return_on_match=True, stop_monitor_on_match=False):
        """
        Monitor the 'monitor' output. Optionally return when call finished message is seen.

        :Parameters:
            :param timeout: (int) Timeout in seconds
            :param pattern: (str) regex pattern to wait for (default: Call Finished)
            :param return_on_match: (bool) return on pattern match (default: True)
            :param stop_monitor_on_match: (bool): stop monitor on pattern match (default: False)

        :Returns:
            Returns the current buffer contents.
        """
        conn = self.connection

        pattern = pattern or pat.call_finished

        call_finished_stmt = Statement(
            pattern=pattern,
            action='send(q)' if stop_monitor_on_match else None,
            args=None,
            loop_continue=False if return_on_match else True,
            continue_timer=True
        )

        dialog = Dialog([call_finished_stmt])
        r = None
        try:
            r = dialog.process(conn.spawn, timeout=timeout, context=self.context)
        except TimeoutError:
            pass

        if r and stop_monitor_on_match:
            conn.sendline()
            conn.state_machine.detect_state(conn.spawn)
            conn.state_machine.go_to('enable', conn.spawn)
        return self.get_buffer()

    def stop(self):
        """ Stop the monitor session and return to enable mode.
        """
        conn = self.connection
        sm = conn.state_machine

        if not self.running:
            conn.log.info('Monitor not running')
            return

        sm.go_to('enable', conn.spawn)
        self.result = self.get_buffer(truncate=True)
        self.result = utils.truncate_trailing_prompt(
            sm.get_state(sm.current_state),
            self.result,
            self.connection.hostname)
        return self.result

    def post_service(self, *args, **kwargs):
        pass
