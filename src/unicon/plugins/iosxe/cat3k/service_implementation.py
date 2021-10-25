__author__ = "Giacomo Trifilo <gtrifilo@cisco.com>"

import re

from time import sleep

from unicon.bases.routers.services import BaseService
from unicon.plugins.generic.service_statements import reload_statement_list
from unicon.plugins.generic.service_implementation import ReloadResult
from unicon.eal.dialogs import Dialog
from unicon.core.errors import SubCommandFailure
from unicon.utils import AttributeDict

from ..statements import boot_from_rommon_stmt
from .service_statements import tcpdump_continue

class Reload(BaseService):
    """Service to reload the device.

    Arguments:
        reload_command: reload command to be issued on device.
            default reload_command is "reload"
        dialog: Dialog which include list of Statements for
            additional dialogs prompted by reload command, in-case
            it is not in the current list.
        timeout: Timeout value in sec, Default Value is 400 sec
        image_to_boot: image to be used if the device stops in rommon mode

    Returns:
        bool: True on success False otherwise

    Raises:
        SubCommandFailure: on failure.

    Example:
        .. code-block:: python

            uut.reload()
            uut.reload(image_to_boot=""tftp://172.18.200.210/image.bin"")
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.RELOAD_TIMEOUT
        self.dialog = Dialog(reload_statement_list + [boot_from_rommon_stmt])

    def call_service(self,
                     reload_command='reload',
                     dialog=Dialog([]),
                     timeout=None,
                     return_output=False,
                     *args, **kwargs):
        con = self.connection
        timeout = timeout or self.timeout
        assert isinstance(dialog,
                          Dialog), "dialog passed must be an instance of Dialog"
        dialog += self.dialog

        con.log.debug(
            "+++ reloading  {}  with reload_command {} and timeout is {} +++"
            .format(self.connection.hostname, reload_command, timeout))

        context = AttributeDict(self.context)
        if "image_to_boot" in kwargs:
            context["image_to_boot"] = kwargs["image_to_boot"]
        con.state_machine.go_to(self.start_state, con.spawn, context=context)
        dialog = self.service_dialog(service_dialog=dialog)
        con.spawn.sendline(reload_command)
        try:
            reload_op=dialog.process(con.spawn, context=context, timeout=timeout,
                prompt_recovery=self.prompt_recovery)
            con.state_machine.go_to('enable', con.spawn,
                                    context=context,
                                    timeout=con.connection_timeout,
                                    prompt_recovery=self.prompt_recovery)
        except Exception as err:
            raise SubCommandFailure("Reload failed : {}".format(err))


        # Issue init commands to disable console logging and perform
        # initial configuration (in case "write erase" was done before reload).
        #
        # This logic is shared with the generic plugin's HAReloadService.
        exec_commands = self.connection.settings.HA_INIT_EXEC_COMMANDS

        for command in exec_commands:
            con.execute(command, prompt_recovery=self.prompt_recovery)
        config_commands = self.connection.settings.HA_INIT_CONFIG_COMMANDS
        config_retry = 0
        while config_retry < \
                self.connection.settings.CONFIG_POST_RELOAD_MAX_RETRIES:
            try:
                con.configure(config_commands, timeout=60,
                    prompt_recovery=self.prompt_recovery)
            except Exception as err:
                if re.search("Config mode locked out", str(err)):
                    sleep(self.connection.settings.\
                        CONFIG_POST_RELOAD_RETRY_DELAY_SEC)
                    con.spawn.sendline()
                    config_retry += 1
            else:
                break

        con.log.debug("+++ Reload Completed Successfully +++")
        self.result = True
        if return_output:
            self.result = ReloadResult(self.result, reload_op.match_output.replace(reload_command, '', 1))


class Shell(BaseService):
    """Service to execute command in the linux shell.

    Arguments:
        command: command to be issued on the linux shell.
        dialog: Dialog which include list of Statements for
            additional dialogs prompted by linux shell, in-case
            it is not in the current list.
        timeout: Timeout value in sec, Default Value is 400 sec

    Returns:
        str: Output of the linux shell command

    Raises:
        SubCommandFailure: on failure.

    Example:
        .. code-block:: python

            result  = uut.shellexec("whoami")
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'shell'
        self.end_state = 'enable'
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.transition_timeout = connection.settings.STATE_TRANSITION_TIMEOUT
        self.shell_enable = False
        self.dialog = Dialog([tcpdump_continue])
        self.__dict__.update(kwargs)

    def pre_service(self, *args, **kwargs):
        if not self.shell_enable:
            self.connection.configure("platform shell")
            self.shell_enable = True

    def call_service(self, command=[],
                     reply=Dialog([]),
                     timeout=None,
                     *args, **kwargs):
        assert isinstance(command, str) or isinstance(command, list)
        con = self.connection
        timeout = timeout or self.timeout

        con.state_machine.go_to(self.start_state, con.spawn,
                                context=self.context, timeout=self.transition_timeout)
        if isinstance(command, str):
            command = [command]

        self.dialog += self.service_dialog(service_dialog=reply)
        for cmd in command:
            con.spawn.sendline(cmd)
            try:
                self.result = self.dialog.process(con.spawn,
                                                  context=self.context,
                                                  timeout=timeout)
            except Exception as err:
                raise SubCommandFailure("Failed to execute command on shell",
                                        err)
            self.result = self.result.match_output.replace(cmd, "").rstrip()
            if self.result.rfind(self.connection.hostname):
                self.result = self.result[:(self.result.rfind(
                    self.connection.hostname) - 1)].strip()


class Rommon(BaseService):
    """Service to execute command in the rommon shell.

    Arguments:
        command: command or list of command to be issued on the rommon shell.
        dialog: Dialog which include list of Statements for
            additional dialogs prompted by rommon shell, in-case
            it is not in the current list.
        timeout: Timeout value in sec, Default Value is 60 sec
        end_state: state where the device should be moved after command
            is executed. This is useful to execute multiple rommon
            commands without exiting rommon mode

    Returns:
        str: Output of the rommon command

    Raises:
        SubCommandFailure: on failure.

    Example:
        .. code-block:: python

            result = uut.rommon("IP_ADDR=172.1.0.1/255.255.0.0")
            result = uut.rommon("BOOT=flash:image.bin", end_state="enable")
    """
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'rommon'
        self.end_state = 'rommon'
        self.local_end_state = None
        self.timeout = connection.settings.EXEC_TIMEOUT

    def pre_service(self, *args, **kwargs):
        if self.connection.state_machine.current_state != "rommon":
            self.connection.configure("boot manual")
        self.connection.state_machine.go_to(self.start_state,
                                            self.connection.spawn,
                                            context=self.context,
                                            timeout=self.connection.settings.RELOAD_TIMEOUT)

    def call_service(self, command=[],
                     reply=Dialog([]),
                     timeout=None,
                     end_state=None,
                     *args, **kwargs):
        assert isinstance(command, str) or isinstance(command, list)
        con = self.connection
        timeout = timeout or self.timeout

        self.local_end_state = end_state
        if isinstance(command, str):
            command = [command]
        self.dialog = self.service_dialog(service_dialog=reply)
        for cmd in command:
            con.spawn.sendline(cmd)
            try:
                self.result = self.dialog.process(con.spawn,
                                                  context=self.context,
                                                  timeout=timeout)
            except Exception as err:
                raise SubCommandFailure("Failed to execute command in rommon",
                                        err)
            self.result = self.result.match_output.replace(cmd, "").rstrip()

    def post_service(self, *args, **kwargs):
        end_state = self.local_end_state or self.end_state
        self.connection.state_machine.go_to(end_state,
                                            self.connection.spawn,
                                            context=self.context,
                                            timeout=self.connection.settings.RELOAD_TIMEOUT)

