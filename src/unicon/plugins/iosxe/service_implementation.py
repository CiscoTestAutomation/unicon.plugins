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
    ResetStandbyRP as GenericResetStandbyRP


from .service_statements import (overwrite_previous, are_you_sure,
    delete_filename, confirm, wish_continue, want_continue)

from unicon.plugins.generic.service_implementation import BashService


# Simplex Services
# ----------------
class Configure(GenericConfigure):
    def call_service(self, command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        super().call_service(command, reply=reply + \
            Dialog([are_you_sure,
                    wish_continue,
                    confirm,
                    want_continue]),
            timeout=timeout, *args, **kwargs)


class Config(Configure):
    def call_service(self, command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        self.connection.log.warn('**** This service is deprecated. ' +
                                 'Please use "configure" service ****')
        super().call_service(command, reply=reply + Dialog([are_you_sure,
                                                            wish_continue,
                                                            confirm,
                                                            want_continue]),
                             timeout=timeout, *args, **kwargs)


class Execute(GenericExecute):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog += Dialog([overwrite_previous,
                               delete_filename,
                               confirm,
                               want_continue])

class Traceroute(GenericTraceroute):
    def call_service(self, addr, command="traceroute", vrf=None, timeout = None,
                     error_pattern=None, **kwargs):
        if 'vrf' not in command and vrf:
            command = command.replace('traceroute', 'traceroute vrf {}'.
                format(str(vrf)))
        super().call_service(addr=addr, command=command,
            error_pattern=error_pattern, timeout=timeout, **kwargs)

class Ping(GenericPing):
    def call_service(self, addr, command="", *, vrf=None, **kwargs):
        command = command if command else \
            "ping vrf {vrf}".format(vrf=vrf) if vrf else "ping"
        super().call_service(addr=addr, command=command, **kwargs)

class Copy(GenericCopy):
    def call_service(self, reply=Dialog([]), vrf=None, *args, **kwargs):
        if vrf is not None:
            kwargs['extra_options'] = kwargs.setdefault('extra_options', '') \
                                      + ' vrf {}'.format(vrf)
        super().call_service(reply=reply, *args, **kwargs)

# HA Services
# -----------
class HAConfigure(GenericHAConfigure):
    def call_service(self, command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        super().call_service(command, reply=reply + \
            Dialog([are_you_sure,
                    wish_continue,
                    confirm,
                    want_continue]),
            timeout=timeout, *args, **kwargs)


class HAConfig(HAConfigure):
    def call_service(self, command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        self.connection.log.warn('**** This service is deprecated. ' +
                                 'Please use "configure" service ****')
        super().call_service(command, reply=reply + \
            Dialog([are_you_sure,
                    wish_continue,
                    confirm,
                    want_continue]),
            timeout=timeout, *args, **kwargs)


class HAExecute(GenericHAExecute):
    def call_service(self, command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        super().call_service(command,
                             reply=reply + Dialog([overwrite_previous,
                                                   delete_filename,
                                                   confirm,
                                                   want_continue]),
                             timeout=timeout, *args, **kwargs)


class HAReload(GenericHAReload):
        # Non-stacked platforms such as ASR and ISR do not use the same
        # reload command as the generic implementation (whose reload command
        # covers stackable platforms only).
    def call_service(self, command=[], reload_command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        if command:
            super().call_service(command or "reload",
                                 timeout=timeout, *args, **kwargs)
        else:
            super().call_service(reload_command=reload_command or "reload",
                                 timeout=timeout, *args, **kwargs)

class HASwitchover(GenericHASwitchover):
    def call_service(self, command=[], dialog=Dialog([]), timeout=None, *args,
                     **kwargs):
        super().call_service(command,
                             dialog = dialog + Dialog([confirm, ]),
                             timeout=timeout, *args, **kwargs)


class BashService(BashService):

    class ContextMgr(BashService.ContextMgr):
        def __init__(self, connection,
                           enable_bash = False,
                           timeout = None):
            super().__init__(connection=connection,
                             enable_bash=enable_bash,
                             timeout=timeout)

        def __enter__(self):
            self.conn.log.debug('+++ attaching bash shell +++')
            # enter shell prompt
            self.conn.state_machine.go_to('shell', self.conn.spawn,
                                     timeout = self.timeout)

            for cmd in self.conn.settings.BASH_INIT_COMMANDS:
                self.conn.execute(
                    cmd, timeout = self.timeout)

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
            reply=reply, timeout=timeout, standby_check='STANDBY HOT',
            *args, **kwargs)
