""" Generic IOS-XE service implementations. """

__author__ = "Myles Dear"


from unicon.eal.dialogs import Dialog

from unicon.plugins.generic.service_implementation import \
    Configure as GenericConfigure, \
    Execute as GenericExecute,\
    Ping as GenericPing,\
    HaConfigureService as GenericHAConfigure,\
    HaExecService as GenericHAExecute,\
    HAReloadService as GenericHAReload,\
    SwitchoverService as GenericHASwitchover, \
    Traceroute as GenericTraceroute, \
    Copy as GenericCopy, \
    ResetStandbyRP as GenericResetStandbyRP, \
    Reload as GenericReload


from .service_statements import execute_statement_list, configure_statement_list, confirm

from .statements import grub_prompt_stmt

from unicon.plugins.generic.service_implementation import BashService as GenericBashService


# Simplex Services
# ----------------
class Configure(GenericConfigure):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dialog += Dialog(configure_statement_list)


class Config(Configure):
    pass


class Execute(GenericExecute):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog += Dialog(execute_statement_list)


class Traceroute(GenericTraceroute):
    def call_service(self, addr, command="traceroute", vrf=None, timeout=None,
                     error_pattern=None, **kwargs):
        if 'vrf' not in command and vrf:
            command = command.replace('traceroute', 'traceroute vrf {}'.format(str(vrf)))
        super().call_service(addr=addr, command=command, error_pattern=error_pattern, timeout=timeout, **kwargs)


class Ping(GenericPing):
    def call_service(self, addr, command="", *, vrf=None, **kwargs):
        command = command if command else "ping vrf {vrf}".format(vrf=vrf) if vrf else "ping"
        super().call_service(addr=addr, command=command, **kwargs)


class Copy(GenericCopy):
    def call_service(self, reply=Dialog([]), vrf=None, *args, **kwargs):
        if vrf is not None:
            kwargs['extra_options'] = kwargs.setdefault('extra_options', '') + ' vrf {}'.format(vrf)
        super().call_service(reply=reply, *args, **kwargs)


# HA Services
# -----------
class HAConfigure(GenericHAConfigure):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog += Dialog(configure_statement_list)


class HAConfig(HAConfigure):
    pass


class HAExecute(GenericHAExecute):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog += Dialog(execute_statement_list)


class HAReload(GenericHAReload):
    # Non-stacked platforms such as ASR and ISR do not use the same
    # reload command as the generic implementation (whose reload command
    # covers stackable platforms only).
    def call_service(self, command=[], reload_command=[], reply=Dialog([]), timeout=None, *args, **kwargs):
        if command:
            super().call_service(command or "reload",
                                 timeout=timeout, *args, **kwargs)
        else:
            super().call_service(reload_command=reload_command or "reload",
                                 timeout=timeout, *args, **kwargs)


class HASwitchover(GenericHASwitchover):
    def call_service(self, command=[], dialog=Dialog([]), timeout=None, *args,
                     **kwargs):
        super().call_service(command, dialog=dialog + Dialog([confirm]), timeout=timeout, *args, **kwargs)


class BashService(GenericBashService):

    class ContextMgr(GenericBashService.ContextMgr):
        def __init__(self, connection, enable_bash=False, timeout=None):
            super().__init__(connection=connection,
                             enable_bash=enable_bash,
                             timeout=timeout)

        def __enter__(self):
            self.conn.log.debug('+++ attaching bash shell +++')
            # enter shell prompt
            self.conn.state_machine.go_to('shell', self.conn.spawn, timeout=self.timeout)

            for cmd in self.conn.settings.BASH_INIT_COMMANDS:
                self.conn.execute(
                    cmd, timeout=self.timeout)

            return self


class ResetStandbyRP(GenericResetStandbyRP):
    """ Service to reset the standby rp.

    Arguments:

        command: command to reset standby, default is"redundancy reload peer"
        dialog: Dialog which include list of Statements for
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
        self.prompt_recovery = connection.prompt_recovery

    def call_service(self, command='redundancy reload peer',
                     reply=Dialog([]),
                     timeout=None,
                     *args,
                     **kwargs):
        super().call_service(command=command,
                             reply=reply,
                             timeout=timeout,
                             standby_check='STANDBY HOT',
                             *args,
                             **kwargs)


class Reload(GenericReload):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)

    def call_service(self,
                     reload_command='reload',
                     dialog=Dialog([]),
                     reply=Dialog([]),
                     timeout=None,
                     return_output=False,
                     reload_creds=None,
                     grub_boot_image=None,
                     *args, **kwargs):

        if grub_boot_image:
            # Add the grub prompt statement
            self.dialog.insert(index=0, statement=grub_prompt_stmt)
            # update the context with the boot_image
            self.context.update({'boot_image': grub_boot_image})

        super().call_service(
            reload_command=reload_command,
            dialog=dialog,
            reply=reply,
            timeout=timeout,
            return_output=return_output,
            reload_creds=reload_creds,
            *args, **kwargs)


class Rommon(GenericExecute):
    """ Brings device to the Rommon prompt and executes commands specified
    """
    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'rommon'
        self.end_state = 'rommon'
        self.service_name = 'rommon'
        self.timeout = 600
        self.__dict__.update(kwargs)
