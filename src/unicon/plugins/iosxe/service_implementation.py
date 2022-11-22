""" Generic IOS-XE service implementations. """

__author__ = "Myles Dear"

import re
from unicon.eal.dialogs import Dialog
from unicon.core.errors import SubCommandFailure

from unicon.plugins.generic.service_implementation import (
    Configure as GenericConfigure,
    Execute as GenericExecute,
    Ping as GenericPing,
    HaConfigureService as GenericHAConfigure,
    HaExecService as GenericHAExecute,
    HAReloadService as GenericHAReload,
    SwitchoverService as GenericHASwitchover,
    Traceroute as GenericTraceroute,
    Copy as GenericCopy,
    ResetStandbyRP as GenericResetStandbyRP,
    Reload as GenericReload,
    Enable as GenericEnable)


from .service_statements import execute_statement_list, configure_statement_list, confirm

from .statements import grub_prompt_stmt

from unicon.plugins.generic.utils import GenericUtils
from unicon.plugins.generic.service_implementation import BashService as GenericBashService


# Simplex Services
# ----------------
class Configure(GenericConfigure):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dialog += Dialog(configure_statement_list)

        class ConfigUtils(GenericUtils):
            def truncate_trailing_prompt(self, con_state,
                                         result,
                                         hostname=None,
                                         result_match=None):
                host_idx = result.rfind(hostname)
                if host_idx != -1:
                    result = result[:host_idx]
                else:
                    if result_match and len(result_match.last_match.groups()) > 2:
                        idx = result.rfind(result_match.last_match.group(2))
                        if idx:
                            result = result[:idx]
                return result

        self.utils = ConfigUtils()


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

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)

    def pre_service(self, *args, **kwargs):
        self.prompt_recovery = self.connection.prompt_recovery
        if 'prompt_recovery' in kwargs:
            self.prompt_recovery = kwargs.get('prompt_recovery')
        self.context.pop('boot_prompt_count', None)
        sm = self.get_sm()
        if sm.current_state != 'rommon':
            return super().pre_service(*args, **kwargs)

    # Non-stacked platforms such as ASR and ISR do not use the same
    # reload command as the generic implementation (whose reload command
    # covers stackable platforms only).
    def call_service(self, command=[], reload_command=[], reply=Dialog([]), timeout=None, *args, **kwargs):
        sm = self.get_sm()

        self.context["image_to_boot"] = \
            kwargs.get("image_to_boot", kwargs.get('image', ''))

        # boot_cmd is used by the boot_image handler, see statements.py
        if sm.current_state == 'rommon' and reload_command:
            self.connection.active.context['boot_cmd'] = reload_command

        if command:
            super().call_service(command or "reload", reply=reply,
                                 timeout=timeout, *args, **kwargs)
        else:
            super().call_service(reload_command=reload_command or "reload", reply=reply,
                                 timeout=timeout, *args, **kwargs)


class HASwitchover(GenericHASwitchover):
    def call_service(self, command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        super().call_service(command, reply=reply + Dialog([confirm]), timeout=timeout, *args, **kwargs)


class BashService(GenericBashService):

    def pre_service(self, *args, **kwargs):
        handle = self.get_handle(kwargs.get('target'))
        if kwargs.get('switch'):
            handle.context['_switch'] = kwargs.get('switch')
        else:
            handle.context.pop('_switch', None)
        if kwargs.get('rp'):
            handle.context['_rp'] = kwargs.get('rp')
        else:
            handle.context.pop('_rp', None)
        super().pre_service(*args, **kwargs)

    class ContextMgr(GenericBashService.ContextMgr):
        def __init__(self, connection, enable_bash=False, timeout=None, **kwargs):
            super().__init__(connection=connection,
                             enable_bash=enable_bash,
                             timeout=timeout,
                             **kwargs)

        def __enter__(self):

            self.conn.log.debug('+++ attaching bash shell +++')
            # enter shell prompt
            self.conn.state_machine.go_to(
                'shell',
                self.conn.spawn,
                timeout=self.timeout,
                context=self.conn.context)

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
        # Add the grub prompt statement
        self.dialog += Dialog([grub_prompt_stmt])

    def pre_service(self, *args, **kwargs):
        self.prompt_recovery = self.connection.prompt_recovery
        if 'prompt_recovery' in kwargs:
            self.prompt_recovery = kwargs.get('prompt_recovery')
        self.context.pop('boot_prompt_count', None)
        sm = self.get_sm()
        if sm.current_state != 'rommon':
            return super().pre_service(*args, **kwargs)

    def call_service(self,
                     reload_command='reload',
                     dialog=Dialog([]),
                     reply=Dialog([]),
                     timeout=None,
                     return_output=False,
                     reload_creds=None,
                     grub_boot_image=None,
                     *args, **kwargs):
        sm = self.get_sm()

        # update the context with the boot_image
        self.context.update({'grub_boot_image': grub_boot_image})

        self.context["image_to_boot"] = \
            kwargs.get("image_to_boot", kwargs.get('image', ''))

        # boot_cmd is used by the boot_image handler, see statements.py
        if sm.current_state == 'rommon' and reload_command != 'reload':
            self.context['boot_cmd'] = reload_command

        super().call_service(
            reload_command=reload_command,
            dialog=dialog,
            reply=reply,
            timeout=timeout,
            return_output=return_output,
            reload_creds=reload_creds,
            *args, **kwargs)

        self.context.pop("image_to_boot", None)
        self.context.pop("grub_boot_image", None)


class Rommon(GenericExecute):
    """ Brings device to the Rommon prompt and executes commands specified
    """
    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'rommon'
        self.end_state = 'rommon'
        self.service_name = 'rommon'
        self.__dict__.update(kwargs)

    def log_service_call(self):
        via = self.handle.via
        alias = self.handle.alias if hasattr(self.handle, 'alias') and self.handle.alias != 'cli' else None
        self.handle.alias
        if alias and via:
            self.connection.log.info(
                "+++ %s with via '%s' and alias '%s': %s +++" %
                (self.connection.hostname if
                 (self.connection.hostname !=
                  self.connection.settings.DEFAULT_LEARNED_HOSTNAME) else "",
                 via, alias, self.service_name))
        elif via:
            self.connection.log.info(
                "+++ %s with via '%s': %s +++" %
                (self.connection.hostname if
                 (self.connection.hostname !=
                  self.connection.settings.DEFAULT_LEARNED_HOSTNAME) else "",
                 via, self.service_name))
        else:
            self.connection.log.info(
                "+++ %s: %s +++" %
                (self.connection.hostname if
                 (self.connection.hostname != self.connection.settings.DEFAULT_LEARNED_HOSTNAME) else "",
                 self.service_name))

    def pre_service(self, *args, **kwargs):
        self.timeout = kwargs.get('reload_timeout', 600)
        sm = self.get_sm()
        con = self.connection
        sm.go_to('enable',
                 con.spawn,
                 context=self.context)
        con.configure('config-register 0x0')
        super().pre_service(*args, **kwargs)


class HARommon(Rommon):
    """ Brings device to the Rommon prompt and executes commands specified
    """
    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'rommon'
        self.end_state = 'rommon'
        self.service_name = 'rommon'
        self.__dict__.update(kwargs)

    def pre_service(self, *args, **kwargs):
        con = self.connection

        # call pre_service to reload to rommon
        super().pre_service(*args, **kwargs)

        # check connection states
        subcon1, subcon2 = list(con._subconnections.values())

        # Check current state
        for subcon in [subcon1, subcon2]:
            subcon.sendline()
            subcon.state_machine.go_to(
                'any',
                subcon.spawn,
                context=subcon.context,
                prompt_recovery=subcon.prompt_recovery,
                timeout=subcon.connection_timeout,
            )
            con.log.debug('{} in state: {}'.format(subcon.alias, subcon.state_machine.current_state))



class Tclsh(Execute):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'tclsh'
        self.end_state = 'tclsh'
        self.service_name = 'tclsh'
        self.__dict__.update(kwargs)
