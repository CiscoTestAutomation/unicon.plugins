__author__ = "dwapstra"

import re
import collections

from unicon.core.errors import SubCommandFailure, StateMachineError
from unicon.bases.routers.services import BaseService
from unicon.eal.dialogs import Dialog, Statement

from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.generic import GenericUtils

from .patterns import StarosPatterns

utils = GenericUtils()


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
        self.service_name = 'command'
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
        self.service_name = 'configure'
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
        except SubCommandFailure as e:
            # Go to exec state after command failure,
            # do not commit changes (handled by state transition)
            sm.go_to(self.end_state, spawn, context=self.context)
            raise

        if len(command_output) == 1:
            self.result = list(command_output.values())[0]
        else:
            self.result = command_output


