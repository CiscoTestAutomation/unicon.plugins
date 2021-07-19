""" ConfD services """

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import re
import collections

from unicon.bases.routers.services import BaseService
from unicon.core.errors import SubCommandFailure, StateMachineError
from unicon.eal.dialogs import Dialog, Statement

from unicon.plugins.generic import service_implementation as GenericServices
from unicon.plugins.generic.statements import GenericStatements, chatty_term_wait
from unicon.plugins.generic.service_statements import execution_statement_list
from unicon.plugins.confd.patterns import ConfdPatterns
from unicon.plugins.generic import GenericUtils


utils = GenericUtils()
statements = GenericStatements()


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
        self.start_state = 'any'
        self.end_state = 'any'

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

        if not isinstance(reply, Dialog):
            raise SubCommandFailure(
                "dialog passed via 'reply' must be an instance of Dialog")

        sm = self.get_sm()
        self.start_state = sm.current_state

        con.log.debug("+++ command '%s' +++" % command)
        timeout = timeout or con.settings.EXEC_TIMEOUT

        if 'service_dialog' in kwargs:
            service_dialog = kwargs['service_dialog']
            if service_dialog is None:
                service_dialog = Dialog([])
            elif not isinstance(service_dialog, Dialog):
                raise SubCommandFailure(
                    "dialog passed via 'service_dialog' must be an instance of Dialog")
            dialog = self.service_dialog(service_dialog=service_dialog+reply)
        else:
            dialog = Dialog(execution_statement_list)
            dialog += self.service_dialog(service_dialog=reply)

        for state in sm.states:
            dialog.append(Statement(pattern=state.pattern))

        con.sendline(command)
        try:
            self.result = dialog.process(con.spawn, timeout=timeout)
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
        self.timeout = connection.settings.CONFIG_TIMEOUT
        self.start_state = 'any'
        self.end_state = 'any'

    def call_service(self, command=[],
                     reply=Dialog([]),
                     timeout=None,
                     error_pattern=None,
                     *args, **kwargs):

        # Get current state of the state machine and determine end state
        sm = self.get_sm()
        con = self.connection

        con.log.debug('+++ configure state %s +++' % sm.current_state)

        if sm.current_cli_style == 'cisco':
            self.start_state = 'cisco_config'
            self.end_state = 'cisco_exec'
            PROMPT_PREFIX = None
        elif sm.current_cli_style == 'juniper':
            self.start_state = 'juniper_config'
            self.end_state = 'juniper_exec'
            PROMPT_PREFIX = con.settings.JUNIPER_PROMPT_PREFIX
        else:
            raise StateMachineError(
                'Invalid state (%s) when calling configure' % sm.current_cli_style())

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

        if con.settings.IGNORE_CHATTY_TERM_OUTPUT:
            # clear buffer of 'System message at ...' messages
            chatty_term_wait(con.spawn, trim_buffer=True)

        command_output = {}
        # if commands is a list
        if not isinstance(command, collections.abc.Sequence):
            raise SubCommandFailure('Invalid command passed %s' % repr(command))

        if 'commit' not in command:
            command.append('commit')

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
                    if PROMPT_PREFIX:
                        output = re.sub(PROMPT_PREFIX, "", output)
                    command_output[cmd] = output.rstrip()
        except SubCommandFailure as e:
            # Go to exec state after command failure,
            # do not commit changes (handled by state transition)
            sm.go_to(self.end_state, spawn, context=self.context)
            raise

        if len(command_output) == 1:
            self.result = list(command_output.values())[0]
        else:
            self.result = command_output


class Execute(GenericServices.Execute):
    """ Execute Service implementation

    Execute service executes commands on the device and returns the console output.
    reply option can be passed for the interactive exec command.

    Arguments:
        command: exec command
        reply: Additional Dialog patterns for interactive exec commands.
        timeout : Timeout value in sec, Default Value is 60 sec

    Returns:
        True on Success,
        raise SubCommandFailure on failure,
        raise StateMachineError if state is not supported.

    Example:
        .. code-block:: python

              output = device.execute("show clock")

    """
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)

    def pre_service(self, command, *args, **kwargs):
        sm = self.get_sm()
        self.saved_cli_style = sm.current_cli_style
        if 'style' in kwargs:
            style = kwargs['style']
            if sm.current_cli_style == 'cisco':
                if style[0].lower() == 'j':
                    self.start_state = "juniper_" + sm.current_cli_mode
            elif sm.current_cli_style == 'juniper':
                if style[0].lower() == 'c':
                    self.start_state = "cisco_" + sm.current_cli_mode
        super().pre_service(*args, **kwargs)

    def post_service(self, *args, **kwargs):
        sm = self.get_sm()
        con = self.connection
        if sm.current_cli_style != self.saved_cli_style:
            con.cli_style(self.saved_cli_style)
        super().post_service(*args, **kwargs)


class CliStyle(BaseService):
    """ Brings device to the given CLI style (Cisco or Juniper)

    Service to change the device CLI mode to the given CLI style in exec or config state.

    Arguments:
        style = Target CLI style ('c' or 'j')

    Returns:
        True on Success
        raise SubCommandFailure on failure
        raise StateMachineError if state is not supported

    Example:
        .. code-block:: python

            ncs.cli_style(style='c')
            ncs.cli_style(style='j')
    """

    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'any'
        self.end_state = 'any'
        self.__dict__.update(kwargs)

    def call_service(self, style, *args, **kwargs):
        # Get current state of the state machine and determine end state
        sm = self.get_sm()
        con = self.connection

        con.log.debug('+++ cli_style current state %s +++' % sm.current_state)
        current_state = sm.current_state
        self.start_state = current_state

        if sm.current_cli_style == 'cisco':
            if style[0].lower() == 'j':
                self.start_state = "juniper_" + sm.current_cli_mode
        elif sm.current_cli_style == 'juniper':
            if style[0].lower() == 'c':
                self.start_state = "cisco_" + sm.current_cli_mode
        else:
            raise StateMachineError('Invalid state when calling cli_style')

        self.end_state = self.start_state
        spawn = self.get_spawn()
        try:
            sm.go_to(self.start_state,
                     spawn,
                     context=self.context)
        except Exception as err:
            raise SubCommandFailure("Failed to bring device to requested CLI state", err)

        con.log.debug('+++ cli_style new state %s +++' % sm.current_state)
        self.result = True
