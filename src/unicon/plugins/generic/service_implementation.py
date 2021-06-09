"""
Module:
    unicon.plugins.generic.service_implementation

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
  This module contains dual-rp and single rp service implementation
  code for generic platform. These services are implemented by subclassing
  BaseService and handle majority of platforms.

"""

import os
import re
import copy
import logging
import collections
import ipaddress
from itertools import chain
import warnings

from time import sleep

from unicon.bases.routers.services import BaseService
from unicon.core.errors import SubCommandFailure, StateMachineError, \
    CopyBadNetworkError, TimeoutError
from unicon.eal.dialogs import Dialog
from unicon.eal.dialogs import Statement
from unicon.plugins.generic.statements import chatty_term_wait, custom_auth_statements
from unicon.plugins.generic.service_statements import reload_statement_list, \
    ping_dialog_list, extended_ping_dialog_list, copy_statement_list, \
    ha_reload_statement_list, switchover_statement_list, \
    standby_reset_rp_statement_list, trace_route_dialog_list
from unicon.plugins.generic.service_patterns import CopyPatterns
from unicon.utils import AttributeDict, to_plaintext
from unicon import logs

from unicon.plugins.generic.utils import GenericUtils
from .service_statements import execution_statement_list, configure_statement_list

utils = GenericUtils()
ReloadResult = collections.namedtuple('ReloadResult', ['result', 'output'])


def invalid_state_change_action(spawn, err_state, sm):
    msg = "Expected device to reach '{}' state, but landed on '{}' state."\
          .format(sm.current_state, err_state.name)
    # Update device current state with unexpected state.
    sm.update_cur_state(err_state)
    raise StateMachineError(msg)


class Send(BaseService):
    """Service to send the command/string with "\\r" to spawned channel.

    If target is passed as standby, command will be sent to standby spawn.

    Arguments:
        command: Command to be sent.
        target: Target connection, Defaults to active.

    Returns:
        True: on Success

    Raises:
        SubCommandFailure: on failure.

    Example:
        .. code-block:: python

            rtr.send("show clock\\r")
            rtr.send("show clock\\r", target='standby')

    """

    def log_service_call(self):
        pass

    def pre_service(self, *args, **kwargs):
        pass

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self, command, target=None, *args, **kwargs):
        spawn = self.get_spawn(target)
        try:
            spawn.send(command, *args, **kwargs)
        except Exception as err:
            raise SubCommandFailure("Failed to send the command to spawn",
                                    err) from err
        self.result = True

    def get_service_result(self):
        return self.result


class Sendline(BaseService):
    """ Sendline Service

    Service to  send the command/string to spawned channel,
    "\\r" will be appended to command by sendline. If target
    is passed as standby, command will be sent to standby
    spawn.

    Arguments:
        command: Command to be sent
        target: Target connection, Defaults to active

    Returns:
        True: on Success

    Raises:
        SubCommandFailureError: On failure of service

    Example:
        .. code-block:: python

            rtr.sendline("show clock")
            rtr.sendline("show clock", target='standby')
    """

    def log_service_call(self):
        pass

    def pre_service(self, *args, **kwargs):
        pass

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self, command='', target=None, *args, **kwargs):
        spawn = self.get_spawn(target)
        try:
            spawn.sendline(command, *args, **kwargs)
        except Exception as err:
            raise SubCommandFailure("Failed to send the command to spawn",
                                    err) from err
        self.result = True

    def get_service_result(self):
        return self.result


class Expect(BaseService):
    """match a list of pattern again the buffer

    Arguments:
        patterns: list of patterns.
        timeout: time to wait for any of the patterns to match.
        size: read size in bytes for reading the buffer.
        trim_buffer: whether to trim the buffer after a successful match.
        target: ``standby`` to match a list of patterns against the buffer on standby spawn channel.
        search_size: maximum size in bytes to search at the end of the buffer

    Returns:
        ExpectMatch instance.
        * It contains the index of the pattern that matched.
        * matched string.
        * re match object.

    Raises:
        TimeoutError: In case no match is found within the timeout period
        or raise SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.sendline("a command")
            rtr.expect([r'^pat1', r'pat2'], timeout=10, target='standby')
    """

    def log_service_call(self):
        pass

    def pre_service(self, *args, **kwargs):
        pass

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self, patterns, timeout=None,
                     size=None, trim_buffer=True,
                     target=None, *args, **kwargs):

        spawn = self.get_spawn(target)
        try:
            self.result = spawn.expect(patterns, timeout, size, *args, **kwargs)
        except Exception as err:
            raise SubCommandFailure("Failed to match buffer on spawn",
                                    err) from err

    def get_service_result(self):
        return self.result


class ReceiveService(BaseService):
    """match a pattern from spawn buffer

    Arguments:
        pattern: regular expression pattern to match. If r'nopattern^' is used then
                 no pattern is match and all data till timeout period will be matched.
        timeout: time to wait for the pattern to match.
        size: read size in bytes for reading the buffer.
        trim_buffer: whether to trim the buffer after a successful match. Default is True.
        target: ``standby`` to match a list of pattern against the buffer on standby spawn channel.
        search_size: maximum size in bytes to search at the end of the buffer

    Returns:
        Bool: True or False
        True: If data is matched by provided pattern.
        False: If nothing is matched by pattern.
        Data matched by pattern is set to receiveBuffer attribute of connection object.

    Raises:
        No Exception is raised if pattern does not get match or timeout happens.
        SubCommandFailure will be raised if any Exception is raised apart from TimeoutError.

    Example:
        .. code-block:: python

            rtr.sendline("a command")
            rtr.receive(r'some_pattern', timeout=10, target='standby')
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)

    def pre_service(self, *args, **kwargs):
        pass

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self, pattern, timeout=None,
                     size=None, trim_buffer=True,
                     target=None, *args, **kwargs):
        spawn = self.get_spawn(target)
        self.result = False
        self.connection.receiveBuffer = ''
        try:
            if pattern == r'nopattern^':
                sleep(timeout or 10)
                self.connection.receiveBuffer = spawn.expect(r'.*', size, *args, **kwargs).match_output
            else:
                self.connection.receiveBuffer = spawn.expect(pattern, timeout, size, *args, **kwargs).match_output
                self.result = True
        except TimeoutError:
            pass
        except Exception as err:
            raise SubCommandFailure("Receive service failed", err) from err

    def get_service_result(self):
        return self.result


class ReceiveBufferService(BaseService):
    """Returns data match by receive() service pattern.

    Returns:
        String: Data matched by receive() service pattern.

    Raises:
        SubCommandFailure: If this is called without calling receive() service.

    Example:
        .. code-block:: python

            rtr.sendline("a command")
            rtr.receive(r'some_pattern', timeout=10, target='standby')
            output = rtr.receive_buffer()
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)

    def pre_service(self, *args, **kwargs):
        pass

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self):
        try:
            self.result = self.connection.receiveBuffer
        except AttributeError as err:
            raise SubCommandFailure("receive_buffer should be invoked after receive call", err)
        except Exception as err:
            raise SubCommandFailure("Error in receive_buffer", err) from err

    def get_service_result(self):
        result = copy.copy(self.result)
        delattr(self.connection, 'receiveBuffer')
        return result


class LogUser(BaseService):
    """ Service to enable or disable a device logs on screen.

    Arguments:
        enable: True/False

    Example:
        .. code-block:: python

            rtr.log_user(enable=True)
            rtr.log_user(enable=False)
    """

    def log_service_call(self):
        pass

    def pre_service(self, *args, **kwargs):
        pass

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self, enable, target=None, *args, **kwargs):
        conn = self.connection

        if enable:
            conn.log.info("+++ log_user: enable +++")

            # does it exist already
            for hdlr in conn.log.handlers:
                if type(hdlr) in (logs.UniconStreamHandler,
                                  logs.UniconScreenHandler):
                    break
            else:
                # add it
                try:
                    from pyats.log import managed_handlers  # noqa
                except Exception:
                    sh = logs.UniconStreamHandler()
                    sh.setFormatter(logging.Formatter(fmt='[%(asctime)s] %(message)s'))
                    conn.log.addHandler(sh)
                else:
                    conn.log.addHandler(logs.UniconScreenHandler())
        else:
            conn.log.info("+++ log_user: disable +++")

            for hdlr in conn.log.handlers:
                if type(hdlr) in (logs.UniconStreamHandler,
                                  logs.UniconScreenHandler):
                    conn.log.removeHandler(hdlr)

        self.result = True

    def get_service_result(self):
        return self.result


class LogFile(BaseService):
    """ Service to get or change Device FileHandler file.
        If no argument passed then it return current filename of FileHandler.
        Return True, if file handlers updated with new filename.

    Arguments:
        filename: file name in which device logs to dump.

    Example:
        .. code-block:: python

            rtr.log_file(filename='/some/path/uut.log')
            rtr.log_file()
    """

    def log_service_call(self):
        pass

    def pre_service(self, *args, **kwargs):
        pass

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self, filename=None, *args, **kwargs):
        conn = self.connection
        file_handler = ''
        self.result = False
        for hdlr in conn.log.handlers:
            if isinstance(hdlr, logs.UniconFileHandler):
                file_handler = hdlr
                break
        if filename:
            filename = os.path.abspath(filename)
            conn.log.info("+++ logfile: {} +++".format(filename))
            if file_handler:
                file_handler.close()
                conn.log.removeHandler(file_handler)
            fh = logs.UniconFileHandler(filename)
            fh.setFormatter(logging.Formatter(fmt='[%(asctime)s] %(message)s'))
            conn.log.addHandler(fh)
            self.result = True
        else:
            if file_handler:
                self.result = file_handler.baseFilename

    def get_service_result(self):
        return self.result


class ExpectLogging(BaseService):
    r""" Service to enable expect internal logging.

    Arguments:
        enable: True/False for enabling and disabling the expect_log

    Example:

        .. code::

            rtr.expect_log(enable=True)
    """

    def log_service_call(self):
        pass

    def pre_service(self, *args, **kwargs):
        pass

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self, enable=False,
                     *args, **kwargs):

        con = self.connection
        if enable:
            con.log.info("+++ enable debug logging +++")
            con.log.setLevel(logging.DEBUG)
        else:
            con.log.info("+++ disable debug logging +++")
            con.log.setLevel(logging.INFO)

        self.result = True

    def get_service_result(self):
        return self.result


class Enable(BaseService):
    """ Brings device to enable

    Service to change the device mode to enable from any state.
    Brings the standby handle to enable state, if standby is passed as input.

    Arguments:
        target= Target connection, Defaults to active

    Returns:
        True on Success, raise SubCommandFailure on failure

    Example:
        .. code-block:: python

            rtr.enable()
            rtr.enable(target='standby')
    """

    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.__dict__.update(kwargs)

    def call_service(self, target=None, command='', *args, **kwargs):
        handle = self.get_handle(target)
        spawn = self.get_spawn(target)
        sm = self.get_sm(target)
        # override command to be enable when command is given
        if command:
            disable = sm.get_state('disable')
            enable = sm.get_state('enable')
            pt = sm.get_path(disable, enable)
            sm.paths[sm.paths.index(pt)].command = command
        try:
            sm.go_to(self.start_state,
                     spawn,
                     context=handle.context)
        except Exception as err:
            raise SubCommandFailure("Failed to Bring device to Enable State",
                                    err) from err
        self.result = True


class Disable(BaseService):
    """Service to change the device to disable mode from any state.

    Brings the standby handle to disable state, if standby is passed as
    input.

    Arguments:
        target: Target connection, Defaults to active

    Returns:
        True on Success, raise SubCommandFailure on failure

    Example:
        .. code-block:: python

            rtr.disable()
            rtr.disable(target='standby')
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'disable'
        self.end_state = 'disable'
        self.__dict__.update(kwargs)

    def call_service(self, target=None, *args, **kwargs):
        handle = self.get_handle(target)
        spawn = self.get_spawn(target)
        sm = self.get_sm(target)
        try:
            sm.go_to(self.start_state,
                     spawn,
                     context=handle.context)
        except Exception as err:
            raise SubCommandFailure("Failed to Bring device to Disable State",
                                    err) from err
        self.result = True


class Execute(BaseService):
    """ Execute Service implementation

    Service  to executes exec_commands on the device and return the
    console output. reply option can be passed for the interactive exec
    command.
    By default, device start state should be same as end state. If device
    ends in some other state, StateMachineError exception is raised. For not to
    raise exception on state change, use allow_state_change=True.

    Arguments:
        command: string or list of strings
        reply: Additional Dialog patterns for interactive exec commands.
        timeout : Timeout value in sec, Default Value is 60 sec
        error_pattern: list of regex to detect command errors
        search_size: maximum size in bytes to search at the end of the buffer
        allow_state_change: Boolean. Default is None. If True, end state can be any state.
        service_dialog: Instance of Dialog that overrides the execute service dialog.
        matched_retries: retry times if state pattern is matched, default is 1
        matched_retry_sleep: sleep between matched_retries, default is 0.05 sec

    Returns:
        String for single command, list for repeated single command,
        dict for multiple commands.

        raises SubCommandFailure on failure
        raises StateMachineError when device fail to reach original state

    Example:
        .. code-block:: python

              output = rtr.execute("show clock")

    """

    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'any'
        self.end_state = 'any'
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.__dict__.update(kwargs)
        self.utils = utils
        self.dialog = Dialog(execution_statement_list)
        self.matched_retries = connection.settings.EXECUTE_MATCHED_RETRIES
        self.matched_retry_sleep = connection.settings.EXECUTE_MATCHED_RETRY_SLEEP

    def log_service_call(self):
        pass

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self, command=[],  # noqa: C901
                     reply=Dialog([]),
                     timeout=None,
                     error_pattern=None,
                     append_error_pattern=None,
                     search_size=None,
                     allow_state_change=None,
                     matched_retries=None,
                     matched_retry_sleep=None,
                     *args, **kwargs):
        con = self.connection
        sm = self.get_sm()
        if allow_state_change is None:
            allow_state_change = con.settings.EXEC_ALLOW_STATE_CHANGE

        timeout = timeout or self.timeout

        if error_pattern is None:
            self.error_pattern = con.settings.ERROR_PATTERN
        else:
            self.error_pattern = error_pattern

        if append_error_pattern:
            if not isinstance(append_error_pattern, list):
                raise ValueError('append_error_pattern should be a list')
            self.error_pattern += append_error_pattern

        # user specified search buffer size
        if search_size is not None:
            con.spawn.search_size = search_size
        else:
            con.spawn.search_size = con.settings.SEARCH_SIZE

        matched_retries = self.matched_retries \
            if matched_retries is None else matched_retries
        matched_retry_sleep = self.matched_retry_sleep \
            if matched_retry_sleep is None else matched_retry_sleep

        if not isinstance(reply, Dialog):
            raise SubCommandFailure(
                "dialog passed via 'reply' must be an instance of Dialog")

        # service_dialog overrides the default execution dialogs
        if 'service_dialog' in kwargs:
            service_dialog = kwargs['service_dialog']
            if service_dialog is None:
                service_dialog = Dialog([])
            elif not isinstance(service_dialog, Dialog):
                raise SubCommandFailure(
                    "dialog passed via 'service_dialog' must be an instance of Dialog")

            dialog = self.service_dialog(
                service_dialog=service_dialog + reply,
                matched_retries=matched_retries,
                matched_retry_sleep=matched_retry_sleep
            )
        else:
            dialog = self.dialog + self.service_dialog(
                service_dialog=reply,
                matched_retries=matched_retries,
                matched_retry_sleep=matched_retry_sleep
            )

            # add default execution statements
            custom_auth_stmt = custom_auth_statements(con.settings.LOGIN_PROMPT,
                                                      con.settings.PASSWORD_PROMPT)
            if custom_auth_stmt:
                dialog += Dialog(custom_auth_stmt)

        # Add all known states to detect state changes.
        for state in sm.states:
            # The current state is already added by the service_dialog method
            if state.name != sm.current_state:
                if allow_state_change:
                    dialog.append(Statement(
                        pattern=state.pattern,
                        matched_retries=matched_retries,
                        matched_retry_sleep=matched_retry_sleep
                    ))
                else:
                    dialog.append(Statement(
                        pattern=state.pattern,
                        action=invalid_state_change_action,
                        args={'err_state': state, 'sm': sm},
                        matched_retries=matched_retries,
                        matched_retry_sleep=matched_retry_sleep
                    ))

        # store the last used dialog, used by unittest
        self._last_dialog = dialog

        if isinstance(command, str):
            if len(command) == 0:
                commands = ['']
            else:
                commands = command.splitlines()
        elif isinstance(command, list):
            commands = command
        else:
            raise ValueError('Command passed is not of type string or list (%s)' % type(command))

        if con.settings.IGNORE_CHATTY_TERM_OUTPUT:
            # clear buffer log messages
            chatty_term_wait(con.spawn, trim_buffer=True)

        command_output = {}
        for command in commands:
            alias = con.via or con.alias
            if alias:
                con.log.info("+++ %s with alias '%s': executing command '%s' +++" % (con.hostname, alias, command))
            else:
                con.log.info("+++ %s: executing command '%s' +++" % (con.hostname, command))
            con.sendline(command)
            try:
                dialog_match = dialog.process(
                    con.spawn,
                    timeout=timeout,
                    prompt_recovery=self.prompt_recovery,
                    context=con.context
                )
                if dialog_match:
                    self.result = dialog_match.match_output
                    self.result = self.get_service_result()
                sm.detect_state(con.spawn, con.context)
            except StateMachineError:
                raise
            except Exception as err:
                raise SubCommandFailure("Command execution failed", err) from err

            if self.result:
                output = self.utils.truncate_trailing_prompt(
                    sm.get_state(sm.current_state),
                    self.result,
                    hostname=con.hostname,
                    result_match=dialog_match,
                )
                output = self.extra_output_process(output)
                output = output.replace(command, "", 1)
                # only strip first newline and leave formatting intact
                output = re.sub(r"^\r?\r\n", "", output, 1)
                output = output.rstrip()

                if command in command_output:
                    if isinstance(command_output[command], list):
                        command_output[command].append(output)
                    else:
                        command_output[command] = [command_output[command], output]
                else:
                    command_output[command] = output

        if len(command_output) == 1:
            self.result = list(command_output.values())[0]
        else:
            self.result = command_output

        # revert search size to default
        con.spawn.search_size = con.settings.SEARCH_SIZE

        if self.end_state != 'any':
            sm.go_to(self.end_state, con.spawn,
                     prompt_recovery=self.prompt_recovery,
                     context=con.context)

    def extra_output_process(self, output):
        # remove backspace and ansi escape sequence from output
        # scenario 1: it prevents correct command replacement, on linux terminals
        # scenario 2: router with '\x1b[KSomething\x08 \x08\x08 \x08\x08 \x08\x08 \x08\x08\x1b[K'
        return utils.remove_backspace_ansi_escape(output)


class Configure(BaseService):
    """Service to configure device with single or list of `commands`.

    Config without config_command will take device to config mode.
    Commands Should be list, if `config_command` are more than one.
    reply option can be passed for the interactive config command.

    Arguments:
        commands : list/single config command
        reply: Addition Dialogs for interactive config commands.
        timeout : Timeout value in sec, Default Value is 30 sec
        error_pattern: list of regex to detect command errors
        target: Target RP where to execute service, for DualRp only
        lock_retries: retry times if config mode is locked, default is 0
        lock_retry_sleep: sleep between retries, default is 2 sec
        bulk: If False, send all commands in one sendline,
              If True, send commands in chunked mode,
              default is False
        bulk_chunk_lines: maximum number of commands to send per chunk,
                          default is 50,
                          0 means to send all commands in a single chunk
        bulk_chunk_sleep: sleep between sending command chunks,
                          default is 0.5 sec

    Returns:
        command output on Success, raise SubCommandFailure on failure

    Example:
        .. code-block:: python

              output = rtr.configure()
              output = rtr.configure('no logging console')
              cmd =['hostname si-tvt-7200-28-41', 'no logging console']
              output = rtr.configure(cmd)
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'config'
        self.end_state = 'enable'
        self.timeout = connection.settings.CONFIG_TIMEOUT
        self.dialog = Dialog(configure_statement_list)
        self.commit_cmd = ''
        self.bulk = connection.settings.BULK_CONFIG
        self.bulk_chunk_lines = connection.settings.BULK_CONFIG_CHUNK_LINES
        self.bulk_chunk_sleep = connection.settings.BULK_CONFIG_CHUNK_SLEEP
        self.valid_transition_commands = ['end', 'exit']
        self.__dict__.update(kwargs)

        class ConfigUtils(GenericUtils):
            def truncate_trailing_prompt(self, con_state,
                                         result,
                                         hostname=None,
                                         result_match=None):
                host_idx = result.rfind(hostname)
                result = result[:host_idx] if host_idx \
                    else result
                return result

        self.utils = ConfigUtils()

    def pre_service(self, *args, **kwargs):
        sm = self.get_sm()

        from_state = sm.get_state(sm.current_state)
        if from_state.name != self.start_state:
            # Allow state change to enable if user provided 'end' or 'exit' command
            # Otherwise raise an exception
            def config_state_change(spawn):
                last_cmd = spawn.last_sent.strip()
                if last_cmd not in self.valid_transition_commands:
                    invalid_state_change_action(
                        spawn, err_state=from_state, sm=sm)
                else:
                    sm.update_cur_state(from_state)

            from_state_stmt = Statement(pattern=from_state.pattern,
                                        action=config_state_change,
                                        args=None,
                                        loop_continue=False)

            self.dialog += Dialog([from_state_stmt])

        self.prompt_recovery = kwargs.get('prompt_recovery', False)

        # Backward compatibility with old config lock implementation
        con = self.connection
        settings = con.settings
        settings.CONFIG_LOCK_RETRIES = kwargs.get('lock_retries', settings.CONFIG_LOCK_RETRIES)
        settings.CONFIG_LOCK_RETRY_SLEEP = kwargs.get('lock_retry_sleep', settings.CONFIG_LOCK_RETRY_SLEEP)

        super().pre_service(*args, **kwargs)

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self,   # noqa: C901
                     command=[],
                     reply=Dialog([]),
                     timeout=None,
                     error_pattern=None,
                     append_error_pattern=None,
                     target=None,
                     bulk=None,
                     bulk_chunk_lines=None,
                     bulk_chunk_sleep=None,
                     *args,
                     **kwargs):
        handle = self.get_handle(target)
        timeout = timeout or self.timeout

        if error_pattern is None:
            self.error_pattern = \
                handle.settings.CONFIGURE_ERROR_PATTERN
        else:
            self.error_pattern = error_pattern

        if append_error_pattern:
            if not isinstance(append_error_pattern, list):
                raise ValueError('append_error_pattern should be a list')
            self.error_pattern += append_error_pattern

        bulk = self.bulk if bulk is None else bulk
        bulk_chunk_lines = self.bulk_chunk_lines \
            if bulk_chunk_lines is None else bulk_chunk_lines
        bulk_chunk_sleep = self.bulk_chunk_sleep \
            if bulk_chunk_sleep is None else bulk_chunk_sleep
        if not isinstance(reply, Dialog):
            raise SubCommandFailure('"reply" must be an instance of Dialog')

        self.result = ''
        if command:
            flat_cmd = self.utils.flatten_splitlines_command(command)
            dialog = self.dialog + self.service_dialog(handle=handle, service_dialog=reply)
            sp = handle.spawn
            if bulk:
                indicator = handle.settings.BULK_CONFIG_END_INDICATOR
                cmd_lst = list(chain(flat_cmd, [indicator]))
                if bulk_chunk_lines == 0:
                    chunks = [cmd_lst]
                else:
                    chunks = [cmd_lst[i:i + bulk_chunk_lines]
                              for i in range(0, len(cmd_lst), bulk_chunk_lines)]
                for idx, chunk in enumerate(chunks, 1):
                    chunk_cmd = '\n'.join(chunk)
                    sp.sendline(chunk_cmd)
                    if idx != len(chunks):
                        sleep(bulk_chunk_sleep)
                        sp.read_update_buffer()
                    else:
                        try:
                            sp.expect([indicator], timeout=timeout,
                                      trim_buffer=False)
                            self.result, _, sp.buffer = \
                                sp.buffer.rpartition(indicator)
                        except Exception as err:
                            raise SubCommandFailure('Configuration failed',
                                                    err) from err
                self.process_dialog_on_handle(handle, dialog, timeout)
                if self.commit_cmd:
                    sp.sendline(self.commit_cmd)
                    self.process_dialog_on_handle(handle, dialog, timeout)
            else:
                cmds = chain(flat_cmd, [self.commit_cmd]) \
                    if self.commit_cmd else flat_cmd
                for cmd in cmds:
                    sp.sendline(cmd)
                    self.update_hostname_if_needed([cmd])
                    self.process_dialog_on_handle(handle, dialog, timeout)

        # store config_result so it can be returned to the user later
        config_result = self.result
        output = handle.state_machine.go_to(
            self.end_state,
            handle.spawn,
            prompt_recovery=self.prompt_recovery,
            timeout=timeout,
            context=self.context
        )
        # set self.result, this is used by get_server_result to check for errors
        self.result = output
        # check for errors in the transition to the end_state
        self.get_service_result()
        # return the config_result to the user via self.result
        self.result = config_result

    def process_dialog_on_handle(self, handle, dialog, timeout):
        try:
            cmd_result = dialog.process(
                handle.spawn,
                timeout=timeout,
                prompt_recovery=self.prompt_recovery,
                context=handle.context
            )
        except Exception as err:
            raise SubCommandFailure('Configuration failed', err) \
                from err

        cmd_result = self.utils.truncate_trailing_prompt(
            handle.state_machine.get_state(handle.state_machine.current_state),
            cmd_result.match_output,
            hostname=handle.hostname,
            result_match=cmd_result)
        self.result += cmd_result
        try:
            self.get_service_result()
        except SubCommandFailure:
            # Go to end state after command failure,
            handle.state_machine.go_to(self.end_state,
                                       handle.spawn,
                                       context=self.context)
            raise

    def update_hostname_if_needed(self, cmd_list):
        for cmd in cmd_list:
            m = re.match(r'^\s*hostname (\S+)', cmd)
            if m:
                self.connection.hostname = m.group(1)
                return


class Config(Configure):

    def call_service(self, *args, **kwargs):
        self.connection.log.warning('**** This service is deprecated. Please use "configure" service ****')
        super().call_service(*args, **kwargs)


class Reload(BaseService):
    """Service to reload the device.

    Arguments:
        reload_command: reload command to be issued. default is "reload"
        reload_creds: credential or list of credentials to use to respond to
                      username/password prompts.
        dialog: Dialog which include list of Statements for
                additional dialogs prompted by reload command, in-case
                it is not in the current list.
        timeout: Timeout value in sec, Default Value is 300 sec
        return_output: If True, return a namedtuple with result and output
                result is True if reload is successful.
                output contains reload command output.

    Returns:
        True on Success, raise SubCommandFailure on failure

    Example ::
        .. code-block:: python

                  rtr.reload()
                  # If reload command is other than 'reload'
                  rtr.reload(reload_command="reload location all", timeout=400)

    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.RELOAD_TIMEOUT
        self.dialog = Dialog(reload_statement_list)
        self.__dict__.update(kwargs)

    def call_service(self,
                     reload_command='reload',
                     dialog=Dialog([]),
                     reply=Dialog([]),
                     timeout=None,
                     return_output=False,
                     reload_creds=None,
                     *args, **kwargs):
        con = self.connection
        timeout = timeout or self.timeout

        fmt_msg = "+++ reloading  %s  " \
                  " with reload_command %s " \
                  "and timeout is %s +++"
        con.log.debug(fmt_msg % (self.connection.hostname,
                                 reload_command,
                                 timeout))

        if reply:
            if dialog:
                con.log.warning("**** Both 'reply' and 'dialog' were provided "
                                "to the reload service.  Ignoring 'dialog'.")
            dialog = reply
        elif dialog:
            warnings.warn('**** "dialog" parameter is deprecated.  '
                          'Use "reply" instead. ****',
                          category=DeprecationWarning)

        if not isinstance(dialog, Dialog):
            raise SubCommandFailure(
                "dialog passed must be an instance of Dialog")

        dialog += self.dialog
        custom_auth_stmt = custom_auth_statements(con.settings.LOGIN_PROMPT, con.settings.PASSWORD_PROMPT)
        if custom_auth_stmt:
            dialog += Dialog(custom_auth_stmt)

        if reload_creds:
            context = self.context.copy()
            context.update(cred_list=reload_creds)
        else:
            context = self.context

        con.spawn.sendline(reload_command)
        try:
            reload_output = dialog.process(con.spawn,
                                           timeout=timeout,
                                           prompt_recovery=self.prompt_recovery,
                                           context=context)
            con.state_machine.go_to(
                'any',
                con.spawn,
                context=self.context,
                prompt_recovery=self.prompt_recovery,
                timeout=con.connection_timeout,
                dialog=con.connection_provider.get_connection_dialog()
            )
            con.state_machine.go_to('enable',
                                    con.spawn,
                                    prompt_recovery=self.prompt_recovery,
                                    context=self.context)
        except Exception as err:
            raise SubCommandFailure("Reload failed %s" % err) from err
        con.state_machine.get_state(self.end_state)
        self.result = True
        if return_output:
            self.result = ReloadResult(self.result, reload_output.match_output.replace(reload_command, '', 1))


class Traceroute(BaseService):
    """ Service to issue traceroute response request to another network from device.

    Returns:
        traceroute command response on Success

    Raises:
        SubCommandFailure on failure

    Example:
        .. code-block:: python

            traceroute(addr="9.33.11.41")
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = 60
        self.dialog = Dialog(trace_route_dialog_list)
        self.__dict__.update(kwargs)

    def call_service(self, addr, command="traceroute", timeout=None, error_pattern=None, **kwargs):
        con = self.connection
        con.log.debug("+++ traceroute +++")

        traceroute_options = ['addr', 'proto', 'ingress', 'source', 'dscp', 'numeric',
                              'timeout', 'probe', 'minimum_ttl', 'maximum_ttl',
                              'port', 'style', 'resolve_as_number']

        if error_pattern is None:
            self.error_pattern = con.settings.TRACEROUTE_ERROR_PATTERN
        else:
            self.error_pattern = error_pattern

        # Default value setting
        timeout = timeout or self.timeout

        trace_route_context = AttributeDict({})

        # Read input values passed
        # Convert to string in case users pass in non-string types such as
        # integer for repeat_count or ipaddress for addr, src_addr or
        # src_route_addr keys.
        # The EAL backend requires all commands to be of string type.
        for key in kwargs:
            if key in traceroute_options:
                trace_route_context[key] = str(kwargs[key])
            else:
                con.log.warning("Unsupported traceroute option {}, ignoring".format(key))

        # Validate Inputs
        if addr:
            # Do string conversion on addr, if specified,
            # in case the user passes in an ipaddress object instead of a
            # string.
            trace_route_context['addr'] = str(addr)
        else:
            raise SubCommandFailure("Address is not specified ")

        # Stringify the command in case it is an object.
        trace_route_str = str(command)
        dialog = self.service_dialog(service_dialog=self.dialog)
        spawn = self.get_spawn()

        spawn.sendline(trace_route_str)
        try:
            self.result = dialog.process(spawn, context=trace_route_context, timeout=timeout)
        except TimeoutError:
            # Recover prompt and re-raise
            # Ctrl+shift+6
            spawn.send('\x1E')
            # Empty buffer
            spawn.expect(".+", trim_buffer=True)
            raise
        except Exception as err:
            raise SubCommandFailure("Traceroute failed", err) from err

        self.result = self.result.match_output
        if self.result.rfind(self.connection.hostname):
            self.result = self.result[:self.result.rfind(self.connection.hostname)]


class Ping(BaseService):
    """ Service to issue ping response request to another network from device.

    Returns:
        ping command response on Success

    Raises:
        SubCommandFailure on failure

    Example:
        .. code-block:: python

            ping(addr="9.33.11.41")
            ping(addr="10.2.1.1", extd_ping='y')

    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = 60
        self.dialog = Dialog(extended_ping_dialog_list)
        # Ping error Patterns
        self.error_pattern = ['^.*(% )?DSCP.*does not match any topology',
                              'Bad IP (A|a)ddress', 'Ping transmit failed',
                              'Invalid vrf', 'Unable to find',
                              'No Route to Host.*',
                              'Destination Host Unreachable',
                              'Unable to initialize Windows Socket Interface',
                              'IP routing table .* does not exist',
                              'Invalid input',
                              'bad context', 'Failed to resolve',
                              '(U|u)nknown (H|h)ost',
                              'Success rate is 0 percent',
                              '100.00% packet loss',
                              '100 % packet loss',
                              'Invalid host']

        self.__dict__.update(kwargs)

    def call_service(self, addr, command="ping", timeout=None, **kwargs):  # noqa: C901
        con = self.connection
        con.log.debug("+++ ping +++")
        # Ping Options
        ping_options = ['multicast', 'transport', 'mask', 'vcid', 'tunnel',
                        'dest_start', 'dest_end', 'exp', 'pad', 'ttl',
                        'reply_mode', 'dscp', 'proto', 'count', 'size',
                        'verbose', 'interval', 'timeout_limit',
                        'send_interval', 'vrf', 'src_route_type',
                        'src_route_addr', 'extended_verbose', 'topo',
                        'validate_reply_data', 'force_exp_null_label',
                        'lsp_ping_trace_rev', 'oif', 'tos', 'data_pat',
                        'int', 'udp', 'precedence', 'novell_type',
                        'extended_timeout_limit', 'sweep_min', 'sweep_max',
                        'sweep_interval', 'src_addr', 'df_bit',
                        'ipv6_ext_headers', 'ipv6_hbh_headers',
                        'ipv6_dst_headers', 'ping_packet_timeout',
                        'sweep_ping', 'timestamp_count', 'record_hops',
                        'ping_failures', 'extd_ping', 'addr'
                        ]

        # Default value setting
        timeout = timeout or self.timeout

        ping_context = AttributeDict({})
        for a in ping_options:
            if a == "novell_type":
                ping_context[a] = "\r"
            elif a == "sweep_ping":
                ping_context[a] = "n"
            elif a == 'extd_ping':
                ping_context[a] = "n"
            else:
                ping_context[a] = ""

        # Read input values passed
        # Convert to string in case users pass in non-string types such as
        # integer for repeat_count or ipaddress for addr, src_addr or
        # src_route_addr keys.
        # The EAL backend requires all commands to be of string type.
        for key in kwargs:
            ping_context[key] = str(kwargs[key])

        # Validate Inputs
        if ping_context['addr'] == "":
            if addr:
                # Do string conversion on addr, if specified,
                # in case the user passes in an ipaddress object instead of a
                # string.
                ping_context['addr'] = str(addr)
            else:
                raise SubCommandFailure("Address is not specified ")

        if ping_context['src_route_type'] != "":
            if ping_context['src_route_addr'] in "":
                raise SubCommandFailure("If src route type is set, "
                                        "then src route addr is mandatory \n")
        elif ping_context['src_route_addr'] != "":
            raise SubCommandFailure("If src route addr is set, "
                                    "then src route type is mandatory \n")
        # Stringify the command in case it is an object.
        ping_str = str(command)

        if ping_context['topo'] != "":
            ping_str = ping_str + "  topo " + ping_context['topo']

        handle = self.get_handle()
        spawn = self.get_spawn()
        if ping_context['extd_ping'].lower().startswith('y'):
            dialog = self.service_dialog(
                handle=handle, service_dialog=self.dialog)
        else:
            dialog = self.service_dialog(
                handle=handle, service_dialog=Dialog(ping_dialog_list))

        spawn.sendline(ping_str)
        try:
            self.result = dialog.process(
                spawn, context=ping_context, timeout=timeout)
        except Exception as err:
            raise SubCommandFailure("Ping failed", err) from err

        self.result = self.result.match_output
        if self.result.rfind(self.connection.hostname):
            self.result = self.result[:self.result.rfind(self.connection.hostname)]


class Copy(BaseService):
    """ Implements Copy service

    Service to support variants of the IOS copy command, which basically
    copies images and configs into and out of router Flash memory.

    Arguments:
        timeout: Timeout value in sec, Default Value is 60 sec

    Returns:
        True on Success, raise SubCommandFailure on failure

    Example:
        .. code-block:python

            out = rtr.copy(source='running-conf',
                         dest='startup-config')

            copy_input = {'source' :'tftp:',
                          'dest':'disk0:',
                          'source_file' : 'copy-test',
                          'dest_file':'copy-test'}
            out = rtr.copy(copy_input)

            out = rtr.copy(source = 'tftp:',
                           dest = 'bootflash:',
                           source_file  = 'copy-test',
                           dest_file = 'copy-test',
                           server='10.105.33.158')
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = 100
        self.dialog = Dialog(copy_statement_list)
        self.copy_pat = CopyPatterns()
        self.interrupt = connection.settings.COPY_INTERRUPT
        self.__dict__.update(kwargs)
        if not hasattr(self, 'max_attempts'):
            self.max_attempts = self.connection.settings.MAX_COPY_ATTEMPTS

    def call_service(self, reply=Dialog([]), *args, **kwargs):  # noqa: C901
        con = self.connection
        # Inputs supported
        copy_options = ['source', 'dest', 'dest_file', 'source_file',
                        'server', 'user', 'password', 'vrf', 'erase',
                        'partition', 'overwrite', 'timeout', 'net_type',
                        'dest_directory']

        # Default values
        copy_context = AttributeDict({})
        for a in copy_options:
            if a == "partition":
                copy_context[a] = 0
            elif a == "erase":
                copy_context[a] = "n"
            elif a == 'overwrite':
                copy_context[a] = True
            elif a == 'vrf':
                copy_context[a] = "Mgmt-intf"
            elif a == 'timeout':
                copy_context[a] = self.timeout
            elif a == 'password':
                password = kwargs.pop('password', None)
                if password:
                    copy_context[a] = to_plaintext(password)
                else:
                    copy_context[a] = ""
            else:
                copy_context[a] = ""

        if not isinstance(reply, Dialog):
            raise SubCommandFailure('reply passed must be instance of Dialog')

        # Read input values passed
        # Stringify input values in case they are objects
        for key in kwargs:
            copy_context[key] = str(kwargs[key])

        if 'max_attempts' in kwargs:
            self.max_attempts = kwargs['max_attempts']

        # Validate input
        if copy_context['source'] == "" or copy_context['dest'] == "":
            raise SubCommandFailure(
                "Source and Destination must be specified ")

        if copy_context['source_file'] == "":
            copy_context['source_file'] = copy_context['source']
        remote_source = ""
        remote_dest = ""
        copy_match = re.search(self.copy_pat.remote_param, copy_context['source'])
        if copy_match:
            remote_source = copy_match.group()
        copy_match = re.search(self.copy_pat.remote_param, copy_context['dest'])
        if copy_match:
            remote_dest = copy_match.group()

        if remote_dest != "" or remote_source != "":
            match_server = ""
            src_server_match = re.search(self.copy_pat.addr_in_remote, copy_context['source'])
            dest_server_match = re.search(self.copy_pat.addr_in_remote, copy_context['dest'])
            if src_server_match or dest_server_match:
                try:
                    match_server = src_server_match.group(2)
                    ipaddress.ip_address(match_server)
                except Exception:
                    try:
                        match_server = dest_server_match.group(2)
                        ipaddress.ip_address(match_server)
                    except Exception:
                        match_server = ""
            if copy_context['server'] == "":
                if match_server == "":
                    raise SubCommandFailure(
                        "Server address must be specified for remote copy")
                else:
                    copy_context['server'] = match_server

        timeout = copy_context['timeout'] or self.timeout

        handle = self.get_handle()
        spawn = self.get_spawn()
        dialog = self.service_dialog(handle=handle, service_dialog=self.dialog)

        dialog = reply + dialog

        copy_string = "copy  " + \
                      copy_context['source'] + " " + copy_context['dest']

        if 'extra_options' in kwargs:
            copy_string = copy_string + " " + kwargs['extra_options']

        if self.max_attempts < 1:
            raise SubCommandFailure(
                "Copy failed : max_attempts must be 1 or greater but "
                "{} was specified.".format(self.max_attempts))

        for retry_num in range(self.max_attempts):
            spawn.sendline(copy_string)
            try:
                self.result = dialog.process(spawn,
                                             context=copy_context,
                                             timeout=timeout)
            except CopyBadNetworkError as err:
                try:
                    # copy_retry_message pattern only trims part of buffer
                    # consume buffer that is remaining there
                    handle.state_machine.go_to('any',
                                               handle.spawn,
                                               context=self.context)
                except Exception:
                    pass
                if retry_num != (self.max_attempts - 1):
                    # wait for a prompt before retry
                    spawn.sendline()
                    handle.state_machine.go_to('any',
                                               handle.spawn,
                                               context=self.context)

                    con.log.info("Copy failure encountered.  Retrying ...")
                else:
                    raise SubCommandFailure("Copy failed", err) from err
            except TimeoutError as err:
                # keep TimeoutError separately, as its consuming buffer part
                # is a best effort and may have different logic later
                # from CopyBadNetworkError
                spawn.send(self.interrupt)
                try:
                    # consume buffer if any is remaining there
                    handle.state_machine.go_to('any',
                                               handle.spawn,
                                               context=self.context)
                except Exception:
                    pass
                if retry_num != (self.max_attempts - 1):
                    # wait for a prompt before retry
                    spawn.sendline()
                    handle.state_machine.go_to('any',
                                               handle.spawn,
                                               context=self.context)
                    con.log.info("Copy dialog timeout encountered.  Retrying ...")
                else:
                    raise SubCommandFailure("Copy failed", err) from err
            except Exception as err:
                try:
                    # copy_error_message pattern may only trim part of buffer
                    # consume buffer if any is remaining there
                    handle.state_machine.go_to('any',
                                               handle.spawn,
                                               context=self.context)
                except Exception:
                    pass
                raise SubCommandFailure("Copy failed", err) from err
            else:
                break

        self.result = self.result.match_output
        if self.result.rfind(self.connection.hostname):
            self.result = self.result[:self.result.rfind(self.connection.hostname)]


class GetMode(BaseService):
    """ Service to get the redundancy mode of the device.

    Returns:
        'sso', 'rpr' or raise SubCommandFailure on failure.

    Example ::
        .. code-block:: python

            rtr.get_mode()
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.__dict__.update(kwargs)

    def call_service(self,
                     timeout=None,
                     utils=utils,
                     *args,
                     **kwargs):

        timeout = timeout or self.timeout
        try:
            self.result = utils.get_redundancy_details(self.connection,
                                                       timeout=timeout)
        except Exception as err:
            raise SubCommandFailure("get_mode failed", err) from err

    def get_service_result(self):
        if 'mode' in self.result:
            return self.result.mode
        else:
            return "None"


class GetRPState(BaseService):
    """ Get Rp state

    Service to get the redundancy state of the device rp.
    Returns  standby rp state if standby is passed as input.

    Arguments:
        target: Service target, by default active

    Returns:
        Expected return values are ACTIVE, STANDBY COLD, STANDBY HOT
        raise SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.get_rp_state()
            rtr.get_rp_state(target='standby')
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.__dict__.update(kwargs)

    def call_service(self,
                     target='active',
                     timeout=None,
                     utils=utils,
                     *args,
                     **kwargs):
        """send the command on the right rp and return the output"""
        handle = self.get_handle(target)

        red_handle = 'my'
        if handle.alias == self.connection.standby.alias:
            red_handle = 'peer'

        try:
            self.result = utils.get_redundancy_details(self.connection, timeout=timeout, who=red_handle)
        except Exception as err:
            raise SubCommandFailure("get_rp_state failed", err) from err

    def get_service_result(self):
        if 'state' in self.result:
            return self.result.state
        else:
            return "None"


class GetConfig(BaseService):
    """Service return running configuration of the device.

    Returns:
        standby running configuration if standby is passed as input.

    Arguments:
        target: Service target, by default active

    Returns:
      running configuration on Success, raise SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.get_config()
            rtr.get_config(target='standby')
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.__dict__.update(kwargs)

    def pre_service(self, *args, **kwargs):
        pass

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self,
                     target='active',
                     timeout=None,
                     *args,
                     **kwargs):
        try:
            self.result = self.connection.execute("show running-config",
                                                  target=target,
                                                  timeout=timeout)
        except Exception as err:
            raise SubCommandFailure("get_config failed", err) from err


class SyncState(BaseService):
    """Bring the device to stable state and re-designate the handles role.

    Returns:
        True on Success, raises SubcommandFailure exception on failure

    Example:
        .. code-block:: python

            rtr.sync_state()
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.__dict__.update(kwargs)

    def pre_service(self, *args, **kwargs):
        self.prompt_recovery = kwargs.get('prompt_recovery', False)

    def call_service(self,
                     target='active',
                     timeout=None,
                     *args,
                     **kwargs):

        con = self.connection
        try:
            # ToDo: Missing code to bring the device to stable state
            self.result = con.connection_provider.designate_handles()
        except Exception as err:
            raise SubCommandFailure("Failed to bring the device to stable state") from err
        self.result = True

    def get_service_result(self):
        return self.result


class HaExecService(BaseService):
    """ DualRp execute service

    Service  to executes exec_commands on the device and return the
    console output. reply option can be passed for the interactive exec
    command. Command will be executed on standby if target is specified
    as standby.

    Arguments:
        command: exec command
        target: Target RP where to execute service
        reply: Additional Dialog( i.e patterns) to be handled
        timeout: Timeout value in sec, Default Value is 60 sec
        matched_retries: retry times if state pattern is matched, default is 1
        matched_retry_sleep: sleep between matched_retries, default is 0.05 sec

    Returns:
        String for single command, list for repeated single command,
        dict for multiple commands.

        raises SubCommandFailure on failure.
        raises StateMachineError when device lands on unexpected state

    Example:
        .. code-block:: python

            output = rtr.execute("show clock")
            output = rtr.execute("show logging", timeout=200)
            output = rtr.execute("show clock", target='standby')
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'any'
        self.end_state = 'any'
        self.__dict__.update(kwargs)
        self.dialog = Dialog(execution_statement_list)

    def log_service_call(self):
        pass

    def pre_service(self, *args, **kwargs):
        self.prompt_recovery = kwargs.get('prompt_recovery', False)

    def post_service(self, *args, **kwargs):
        pass

    def call_service(self, command,
                     reply=Dialog([]),
                     target='active',
                     timeout=None,
                     error_pattern=None,
                     search_size=None,
                     allow_state_change=None,
                     matched_retries=None,
                     matched_retry_sleep=None,
                     *args,
                     **kwargs):
        """send the command on the right rp and return the output"""
        # create an alias for connection.
        handle = self.get_handle(target)

        self.result = handle.execute(command,
                                     reply=reply,
                                     timeout=timeout,
                                     error_pattern=error_pattern,
                                     search_size=search_size,
                                     allow_state_change=allow_state_change,
                                     matched_retries=matched_retries,
                                     matched_retry_sleep=matched_retry_sleep,
                                     *args,
                                     **kwargs)


class HaConfigureService(Configure):
    """DualRp configure service
    Service to configure device with single or list of `commands`.

    Config without config_command will take device to config mode.
    Commands Should be list, if `config_command` are more than one.
    reply option can be passed for the interactive config command.
    Command can be executed on standby by pass in target as standby.

    Arguments:
        commands : list/single config command
        reply: Addition Dialogs for interactive config commands.
        timeout : Timeout value in sec, Default Value is 30 sec
        target: Target RP where to execute service
        lock_retries: retry times if config mode is locked, default is 0
        lock_retry_sleep: sleep between retries, default is 2 sec
        bulk: send commands in one sendline or not, default is False

    Returns:
        command output on Success, raise SubCommandFailure on failure

    Example:
        .. code-block:: python

              output = rtr.configure()
              output = rtr.configure('no logging console')
              cmd =['hostname si-tvt-7200-28-41', 'no logging console']
              output = rtr.configure(cmd)
              output = rtr.configure(cmd, target='standby')
    """
    pass


class HaConfigure(HaConfigureService):

    def call_service(self, *args, **kwargs):
        self.connection.log.warning('**** This service is deprecated. ' +
                                    'Please use "configure" service ****')
        super().call_service(*args, **kwargs)


# TODO Add option to take additional dialog
class HAReloadService(BaseService):
    """ Service to reload the device.

    Arguments:
        reload_command: reload command to be used. default "redundancy reload shelf"
        reload_creds: credential or list of credentials to use to respond to
                      username/password prompts.
        reply: Additional Dialog( i.e patterns) to be handled
        timeout: Timeout value in sec, Default Value is 60 sec
        return_output: if True, return namedtuple with result and reload output

    Returns:
        console True on Success, raises SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.reload()
            # If reload command is other than 'redundancy reload shelf'
            rtr.reload(reload_command="reload location all", timeout=700)
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.HA_RELOAD_TIMEOUT
        self.dialog = Dialog(ha_reload_statement_list)
        self.command = 'reload'
        self.__dict__.update(kwargs)

    def call_service(self,  # noqa: C901
                     command=None,
                     reload_command=None,
                     dialog=Dialog([]),
                     reply=Dialog([]),
                     target='active',
                     timeout=None,
                     return_output=False,
                     reload_creds=None,
                     target_standby_state='STANDBY HOT',
                     *args,
                     **kwargs):

        con = self.connection
        if reply:
            if dialog:
                con.log.warning("**** Both 'reply' and 'dialog' were provided "
                                "to the reload service.  Ignoring 'dialog'.")
            dialog = reply
        elif dialog:
            warnings.warn('**** "dialog" parameter is deprecated.  '
                          'Use "reply" instead. ****',
                          category=DeprecationWarning)

        timeout = timeout or self.timeout
        if command:
            con.log.warning("*** HA reload() service 'command' parameter "
                            "will be deprecated in next release. "
                            "Please use 'reload_command' parameter ***")
        if command and reload_command:
            raise SubCommandFailure(
                "Please use either 'command' or 'reload_command' parameter")
        command = command or reload_command or self.command

        # TODO counter value must be moved to settings
        counter = 0
        fmt_str = "+++ reloading  %s  with reload_command %s and timeout is %s +++"
        con.log.debug(fmt_str % (con.hostname, command, timeout))
        dialog += self.dialog
        dialog = self.service_dialog(handle=con.active,
                                     service_dialog=dialog)
        custom_auth_stmt = custom_auth_statements(con.settings.LOGIN_PROMPT, con.settings.PASSWORD_PROMPT)

        if reload_creds:
            context = con.active.context.copy()
            context.update(cred_list=reload_creds)
            sby_context = con.standby.context.copy()
            sby_context.update(cred_list=reload_creds)
        else:
            context = con.active.context
            sby_context = con.standby.context

        if custom_auth_stmt:
            dialog += Dialog(custom_auth_stmt)
        con.active.state_machine.go_to('enable',
                                       con.active.spawn,
                                       prompt_recovery=self.prompt_recovery,
                                       context=context)

        # Issue reload command
        con.active.spawn.sendline(command)
        try:
            reload_output = dialog.process(con.active.spawn,
                                           context=context,
                                           prompt_recovery=self.prompt_recovery,
                                           timeout=timeout)
            con.active.state_machine.go_to('any',
                                           con.active.spawn,
                                           prompt_recovery=self.prompt_recovery,
                                           timeout=con.connection_timeout,
                                           context=context)

            # Bring standby to good state.
            con.log.info('Waiting for config sync to finish')
            standby_wait_time = con.settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT
            standby_wait_interval = 50
            standby_sync_try = standby_wait_time // standby_wait_interval + 1
            for round in range(standby_sync_try):
                con.standby.spawn.sendline()
                try:
                    con.standby.state_machine.go_to(
                        'any',
                        con.standby.spawn,
                        context=sby_context,
                        timeout=standby_wait_interval,
                        prompt_recovery=self.prompt_recovery,
                        dialog=con.connection_provider.get_connection_dialog()
                    )
                    break
                except Exception as err:
                    if round == standby_sync_try - 1:
                        raise Exception(
                            'Bringing standby to any state failed within {} sec'.format(standby_wait_time)) from err

        except Exception as err:
            raise SubCommandFailure("Reload failed : %s" % err) from err

        # Re-designate handles before applying config.
        # Roles could have switched as a result of the reload.
        con.connection_provider.designate_handles()

        con.active.state_machine.go_to('enable',
                                       con.active.spawn,
                                       prompt_recovery=self.prompt_recovery,
                                       context=context)

        # Issue init commands to disable console logging
        exec_commands = con.active.settings.HA_INIT_EXEC_COMMANDS
        for exec_command in exec_commands:
            con.execute(exec_command, prompt_recovery=self.prompt_recovery)
        config_commands = con.active.settings.HA_INIT_CONFIG_COMMANDS

        config_lock_retries_ori = con.settings.CONFIG_LOCK_RETRIES
        config_lock_retry_sleep_ori = con.settings.CONFIG_LOCK_RETRY_SLEEP
        con.active.settings.CONFIG_LOCK_RETRY_SLEEP = con.active.settings.CONFIG_POST_RELOAD_RETRY_DELAY_SEC
        con.active.settings.CONFIG_LOCK_RETRIES = con.active.settings.CONFIG_POST_RELOAD_MAX_RETRIES

        try:
            con.configure(config_commands,
                          target='active',
                          prompt_recovery=self.prompt_recovery)
        except Exception:
            raise
        finally:
            con.settings.CONFIG_LOCK_RETRIES = config_lock_retries_ori
            con.settings.CONFIG_LOCK_RETRY_SLEEP = config_lock_retry_sleep_ori

        # best effort for 'STANDBY HOT', consider argument for mandatory/ignore
        while counter < 31:
            try:
                # TODO need fix iosxr get_rp_state service
                rp_state = con.get_rp_state(target='standby', timeout=30)
                if rp_state.find(target_standby_state) != -1:
                    con.log.info('Standby RP State: {}'.format(rp_state))
                    counter = 32
                else:
                    con.log.info('Standby RP State: {}, waiting for {}'.format(rp_state, target_standby_state))
                    sleep(6)
                    counter += 1
            except Exception as err:
                con.log.error('Failed to get RP state: {}'.format(err))
                sleep(6)
                counter += 1

        con.disconnect()
        con.connect()
        con.log.info("+++ Reload Completed Successfully +++")
        self.result = True
        if return_output:
            self.result = ReloadResult(self.result, reload_output.match_output.replace(command, '', 1))


class SwitchoverService(BaseService):
    """ Service to switchover the device.

    Arguments:
        command: command to do switchover. default
                 "redundancy force-switchover"
        switchover_creds: credential or list of credentials to use to respond to
                      username/password prompts.
        dialog: Dialog which include list of Statements for
                additional dialogs prompted by switchover command,
                in-case it is not in the current list.
        timeout: Timeout value in sec, Default Value is 500 sec

    Returns:
        True on Success, raise SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.switchover()
            # If switchover command is other than 'redundancy force-switchover'
            rtr.switchover(command="command which invoke switchover",
            timeout=700)
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.SWITCHOVER_TIMEOUT
        self.dialog = Dialog(switchover_statement_list)
        self.command = 'redundancy force-switchover'
        self.__dict__.update(kwargs)

    def call_service(self, command=None,  # noqa: C901
                     dialog=Dialog([]),
                     reply=Dialog([]),
                     timeout=None,
                     sync_standby=True,
                     switchover_creds=None,
                     *args,
                     **kwargs):
        # create an alias for connection.
        con = self.connection
        if reply:
            if dialog:
                con.log.warning("**** Both 'reply' and 'dialog' were provided "
                                "to the reload service.  Ignoring 'dialog'.")
            dialog = reply
        elif dialog:
            warnings.warn('**** "dialog" parameter is deprecated.'
                          ' Please use "reply" ****',
                          category=DeprecationWarning)

        timeout = timeout or self.timeout
        command = command or self.command
        switchover_counter = con.settings.SWITCHOVER_COUNTER
        con.log.debug("+++ Issuing switchover on  %s  with "
                      "switchover_command %s and timeout is %s +++"
                      % (con.hostname, command, timeout))

        # Check is switchover possible?
        rp_state = con.get_rp_state(target='standby', timeout=100)
        if rp_state.find('STANDBY HOT') == -1:
            raise SubCommandFailure(
                "Switchover can't be issued in %s state" % rp_state)

        # Save current active and standby handle details
        standby_start_cmd = con.standby.start
        dialog += self.dialog
        dialog = self.service_dialog(handle=con.active,
                                     service_dialog=dialog)
        custom_auth_stmt = custom_auth_statements(con.settings.LOGIN_PROMPT, con.settings.PASSWORD_PROMPT)
        if custom_auth_stmt:
            dialog += Dialog(custom_auth_stmt)

        # Use the standby credentials when processing because any
        # authentication request is expected to come from the new active.
        if switchover_creds:
            context = con.standby.context.copy()
            context.update(cred_list=switchover_creds)
        else:
            context = con.standby.context

        # Issue switchover command
        con.active.spawn.sendline(command)
        try:
            dialog.process(con.active.spawn,
                           timeout=timeout,
                           prompt_recovery=self.prompt_recovery,
                           context=context)
        except TimeoutError:
            pass
        except SubCommandFailure as err:
            raise SubCommandFailure("Switchover Failed %s" % str(err)) from err

        # Initialise Standby
        try:
            con.standby.spawn.sendline("\r")
            con.standby.spawn.expect(".*")
            con.swap_roles()
        except Exception as err:
            raise SubCommandFailure("Failed to initialise the standby",
                                    err) from err

        counter = 0
        if not sync_standby:
            con.log.info("Standby state check disabled on user request")

        else:
            while counter < switchover_counter:
                con.active.spawn.sendline("\r")
                con.active.spawn.expect(".*")
                try:
                    rp_state = con.get_rp_state(target='standby',
                                                timeout=60)
                except (SubCommandFailure, TimeoutError):
                    sleep(9)
                    counter += 1
                    continue
                except Exception:
                    con.active.spawn.sendline("\r")
                    con.active.spawn.expect(".*")
                    continue
                else:
                    if re.search('STANDBY HOT', rp_state):
                        counter = switchover_counter + 1
                    else:
                        sleep(9)
                        counter += 1

            con.active.state_machine.go_to(
                'any',
                con.active.spawn,
                context=context,
                prompt_recovery=self.prompt_recovery,
                timeout=con.connection_timeout,
                dialog=con.connection_provider.get_connection_dialog()
            )
            con.active.state_machine.go_to(
                'enable',
                con.active.spawn,
                context=context,
                prompt_recovery=self.prompt_recovery
            )

            # Issue init commands to disable console logging
            exec_commands = self.connection.settings.HA_INIT_EXEC_COMMANDS
            for command in exec_commands:
                con.execute(command, prompt_recovery=self.prompt_recovery)
            config_commands = self.connection.settings.HA_INIT_CONFIG_COMMANDS
            config_retry = 0
            while config_retry < 20:
                try:
                    con.configure(config_commands,
                                  prompt_recovery=self.prompt_recovery)
                except Exception as err:
                    if re.search("Config mode cannot be entered",
                                 str(err)):
                        sleep(9)
                        con.active.spawn.sendline()
                        config_retry += 1
                else:
                    config_retry = 21

            # Clear Standby buffer
            con.standby.spawn.sendline("\r")
            con.standby.spawn.expect(".*")
            try:
                con.standby.state_machine.go_to('any',
                                                con.standby.spawn,
                                                context=con.standby.context,
                                                dialog=con.connection_provider.get_connection_dialog())
            except Exception:
                con.log.error("Failed to bring standby rp to any state")
                raise

            con.enable(target='standby')
        # Verify switchover is Successful
        if con.active.start == standby_start_cmd:
            con.log.info("Switchover is Successful")
            self.result = True
        else:
            con.log.info("Switchover is Failed")
            self.result = False


class ResetStandbyRP(BaseService):
    """ Service to reset the standby rp.

    Arguments:

        command: command to reset standby, default is"redundancy reload peer"
        reply: Dialog which include list of Statements for
                 additional dialogs prompted by standby reset command,
                 in-case it is not in the current list.
        timeout: Timeout value in sec, Default Value is 500 sec

    Returns:
        True on Success, raise SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.reset_standby_rp()
            # If command is other than 'redundancy reload peer'
            rtr.reset_standby_rp(command="command which will reset standby rp",
            timeout=600)

    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.HA_RELOAD_TIMEOUT
        self.dialog = Dialog(standby_reset_rp_statement_list)
        self.__dict__.update(kwargs)

    def pre_service(self, *args, **kwargs):
        self.prompt_recovery = kwargs.get('prompt_recovery', False)
        if self.connection.is_connected:
            return
        elif self.connection.reconnect:
            self.connection.connect()
        else:
            raise ConnectionError("Connection is not established to device")
        state_machine = self.connection.active.state_machine
        state_machine.go_to(self.start_state,
                            self.connection.active.spawn,
                            context=self.connection.context)

    def post_service(self, *args, **kwargs):
        state_machine = self.connection.active.state_machine
        state_machine.go_to(self.end_state,
                            self.connection.active.spawn,
                            context=self.connection.context)

    def call_service(self, command='redundancy reload peer',  # noqa: C901
                     reply=Dialog([]),
                     timeout=None,
                     *args,
                     **kwargs):
        # create an alias for connection.
        con = self.connection
        timeout = timeout or self.timeout
        # resetting the standby rp for
        con.log.debug("+++ Issuing reset on  %s  with "
                      "reset_command %s and timeout is %s +++"
                      % (con.hostname, command, timeout))

        # Check is it possible to reset the standby?
        rp_state = con.get_rp_state(target='standby', timeout=100)

        if re.search('DISABLED', rp_state):
            raise SubCommandFailure("No Standby found")

        if 'standby_check' in kwargs and not re.search(kwargs['standby_check'], rp_state):
            raise SubCommandFailure("Standby found but not in the expected state")

        dialog = self.service_dialog(handle=con.active,
                                     service_dialog=self.dialog)
        # Issue standby reset command
        con.active.spawn.sendline(command)
        try:
            dialog.process(con.active.spawn,
                           timeout=30,
                           context=con.active.context)
        except TimeoutError:
            pass
        except SubCommandFailure as err:
            raise SubCommandFailure("Failed to reset standby rp %s" % str(err)) from err

        reset_counter = timeout / 10

        counter = 0
        reloadGood = False
        while counter < reset_counter:
            try:
                rp_state = con.get_rp_state(target='standby',
                                            timeout=60)
            except (SubCommandFailure, TimeoutError):
                sleep(10)
                counter += 1
                continue
            else:
                # first need to insure reload happens
                # no false positives
                if not reloadGood:
                    if not re.search('DISABLED', rp_state):
                        sleep(2)
                        counter += 1
                        continue
                    else:
                        reloadGood = True
                        counter = 0

                if re.search('STANDBY HOT', rp_state):
                    counter = reset_counter + 1
                else:
                    sleep(10)
                    counter += 1

        # Clear Standby buffer
        try:
            con.standby.spawn.sendline("\r")
            con.standby.spawn.expect(".*")
            con.standby.state_machine._current_state = 'disable'
            con.enable(target='standby')
        except SubCommandFailure as err:
            raise SubCommandFailure("Failed to bring standby to enable: %s" %
                                    str(err)) from err
        con.log.info("Successfully reloaded Standby RP")
        self.result = True


class BashService(BaseService):
    """ Service to provide an console to do shell commands

    Arguments:
        None

    Returns:
        AttributeError: No attributes

    Example:
        .. code-block:: python

            rtr.bash_console(timeout=60).execute('ls')

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_state = "enable"
        self.end_state = "enable"
        self.bash_enabled = False

    def pre_service(self, *args, **kwargs):
        """ Common pre_service procedure for all Services """
        self.prompt_recovery = kwargs.get('prompt_recovery', False)
        if self.connection.is_connected:
            return
        elif self.connection.reconnect:
            self.connection.connect()
        else:
            raise ConnectionError("Connection is not established to device")
        if 'target' in kwargs:
            handle = self.get_handle(kwargs['target'])
        else:
            handle = self.get_handle()
        handle.state_machine.go_to(
            self.start_state,
            handle.spawn,
            context=self.connection.context,
            prompt_recovery=self.prompt_recovery
        )

    def call_service(self, target=None, **kwargs):
        handle = self.get_handle(target)
        self.result = self.__class__.ContextMgr(connection=handle, enable_bash=not self.bash_enabled, **kwargs)

        # if bash wasn't enabled, it is now!
        if not self.bash_enabled:
            self.bash_enabled = True

    def post_service(self, *args, **kwargs):
        if 'target' in kwargs:
            handle = self.get_handle(kwargs['target'])
        else:
            handle = self.get_handle()
        handle.state_machine.go_to(
            self.start_state,
            handle.spawn,
            context=self.connection.context,
            prompt_recovery=self.prompt_recovery
        )

    class ContextMgr(object):
        def __init__(self, connection, enable_bash=False, timeout=None):
            self.conn = connection
            # Specific platforms has its own prompt
            self.enable_bash = enable_bash
            self.timeout = timeout or connection.settings.CONSOLE_TIMEOUT

        def __enter__(self):
            raise NotImplementedError('No enter shell method supports in platform {}'.format(self.conn.os))

        def __exit__(self, exc_type, exc_value, exc_tb):
            self.conn.log.debug('--- detaching console ---')

            sm = self.conn.state_machine
            sm.go_to('enable', self.conn.spawn)

            # do not suppress
            return False

        def __getattr__(self, attr):
            if attr in ('execute', 'sendline', 'send', 'expect'):
                return getattr(self.conn, attr)

            raise AttributeError('%s object has no attribute %s'
                                 % (self.__class__.__name__, attr))


class AttachModuleService(BaseService):
    """ Service to connect to a device module and execute commands.

    Arguments:
        None

    Returns:
        AttributeError: No attributes

    Examples:
        .. code-block:: python

            rtr.attach(1, timeout=60).execute('show interface')

            with rtr.attach(1) as m:
                m.execute('show interface')
                m.execute(['show interface 1', 'show interface 2'])

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_state = "module"
        self.end_state = "enable"
        self.service_name = "attach"

    def pre_service(self, module_num, *args, **kwargs):
        """ Common pre_service procedure for all Services """
        self.prompt_recovery = kwargs.get('prompt_recovery', False)
        if self.connection.is_connected:
            return
        elif self.connection.reconnect:
            self.connection.connect()
        else:
            raise ConnectionError("Connection is not established to device")
        self.context._module_num = module_num

    def call_service(self, module_num, **kwargs):
        self.result = self.__class__.ContextMgr(self.connection,
                                                module_num,
                                                context=self.context,
                                                **kwargs)

    class ContextMgr(object):
        def __init__(self,
                     connection,
                     module_num,
                     target='active',
                     context=None,
                     timeout=None):
            self.conn = connection
            # Specific platforms has its own prompt
            self.timeout = timeout
            self.target = target
            self.context = context
            self.timeout = timeout or connection.settings.CONSOLE_TIMEOUT
            self.context._module_num = module_num

        def __enter__(self):
            if self.conn.is_ha:
                if self.target == 'standby':
                    conn = self.conn.standby
                elif self.target == 'active':
                    conn = self.conn.active
            else:
                conn = self.conn

            if 'module' not in [s.name for s in conn.state_machine.states]:
                raise NotImplementedError('Attach module state not implemented')

            self.conn.log.debug('+++ attaching module +++')
            conn.state_machine.go_to('module',
                                     conn.spawn,
                                     context=self.context,
                                     timeout=self.timeout)

            return self

        def __exit__(self, exc_type, exc_value, exc_tb):
            self.conn.log.debug('--- detaching module ---')

            if self.conn.is_ha:
                if self.target == 'standby':
                    conn = self.conn.standby
                elif self.target == 'active':
                    conn = self.conn.active
            else:
                conn = self.conn

            sm = conn.state_machine
            sm.go_to('enable', conn.spawn)

            # do not suppress
            return False

        def __getattr__(self, attr):
            if attr in ('execute', 'sendline', 'send', 'expect'):
                return getattr(self.conn, attr)

            raise AttributeError('%s object has no attribute %s'
                                 % (self.__class__.__name__, attr))


class Switchto(BaseService):
    """ Switch to a certain CLI state that is known to the statemachine
    """

    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.service_name = 'switchto'
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.context = context

    def log_service_call(self):
        pass

    def pre_service(self, to_state, *args, **kwargs):

        if not self.connection.connected:
            self.connection.log.warning('Device is not connected, ignoring switchto')
            return

        self.connection.log.info("+++ %s: %s +++" % (self.service_name, to_state))

    def call_service(self, to_state,
                     timeout=None,
                     *args, **kwargs):

        if not self.connection.connected:
            return

        con = self.connection
        sm = self.get_sm()

        timeout = timeout if timeout is not None else self.timeout

        if isinstance(to_state, str):
            to_state_list = [to_state]
        elif isinstance(to_state, list):
            to_state_list = to_state
        else:
            raise Exception('Invalid switchto to_state type: %s' % repr(to_state))

        for to_state in to_state_list:
            to_state = to_state.replace(' ', '_')

            valid_states = [x.name for x in sm.states]
            if to_state not in valid_states:
                con.log.warning('%s is not a valid state, ignoring switchto' % to_state)
                return

            con.state_machine.go_to(to_state, con.spawn,
                                    context=self.context,
                                    hop_wise=True,
                                    timeout=timeout)

        self.end_state = sm.current_state

    def post_service(self, *args, **kwargs):
        pass

