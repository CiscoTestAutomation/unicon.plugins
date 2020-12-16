"""
Module:
    unicon.plugins.iosxr.ncs5k.service_implementation

Description:
  This module NCS5K specific service implementation

"""
__author__ = "dwapstra"

import re
from time import sleep

from unicon.bases.routers.services import BaseService
from unicon.core.errors import SubCommandFailure, TimeoutError
from unicon.eal.dialogs import Dialog

from .service_statements import reload_statement_list, reload_statement_list_vty


class Reload(BaseService):
    """Service to reload the device.

    Arguments:
        reload_command: reload command to be issued. default is "reload"
        dialog: Dialog which include list of Statements for
                additional dialogs prompted by reload command, in-case
                it is not in the current list.
        timeout: Timeout value in sec, Default Value is 300 sec
        reload_creds: name or list of names of credential(s) to use if
                      username or password is prompted for during reload.

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
                     timeout=None,
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

        con.state_machine.go_to(self.start_state,
                                con.spawn,
                                prompt_recovery=self.prompt_recovery,
                                context=self.context)

        if not isinstance(dialog, Dialog):
            raise SubCommandFailure(
                "dialog passed must be an instance of Dialog")

        show_terminal = con.execute('show terminal')
        line_type = re.search(r"Line .*, Type \"(\w+)\"", show_terminal)
        if line_type and line_type.groups():
            line_type = line_type.group(1)

        if reload_creds:
            context = self.context.copy()
            context.update(cred_list=reload_creds)
        else:
            context = self.context

        if line_type == 'Console':
            dialog += self.dialog
            con.spawn.sendline(reload_command)
            try:
                self.result = dialog.process(con.spawn,
                               timeout=timeout,
                               prompt_recovery=self.prompt_recovery,
                               context=context)
                if self.result:
                    self.result = self.result.match_output
                con.state_machine.go_to('any',
                                        con.spawn,
                                        prompt_recovery=self.prompt_recovery,
                                        context=self.context)
            except Exception as err:
                raise SubCommandFailure("Reload failed %s" % err)

            output = self.result
            output = output.replace(reload_command, "", 1)
            # only strip first newline and leave formatting intact
            output = re.sub(r"^\r?\r\n", "", output, 1)
            output = output.rstrip()
        else:
            con.log.warning('Did not detect a console session, will try to reconnect...')
            dialog = Dialog(reload_statement_list_vty)
            con.spawn.sendline(reload_command)
            output = ""
            self.result = dialog.process(con.spawn,
                           timeout=timeout,
                           prompt_recovery=self.prompt_recovery,
                           context=self.context)
            if self.result:
                output += self.result.match_output
            try:
                m = con.spawn.expect('.+', timeout=10)
                if m:
                    output += m.match_output
            except TimeoutError:
                pass
            con.log.warning('Disconnecting...')
            con.disconnect()
            for x in range(con.settings.RELOAD_RECONNECT_ATTEMPTS):
                con.log.warning('Waiting for {} seconds'.format(con.settings.RELOAD_WAIT))
                sleep(con.settings.RELOAD_WAIT)
                con.log.warning('Trying to connect... attempt #{}'.format(x+1))
                try:
                    output += con.connect()
                except:
                    con.log.warning('Connection failed')
                if con.is_connected:
                    break

            if not con.is_connected:
                raise SubCommandFailure('Reload failed - could not reconnect')

        self.result = output

class HAReload(BaseService):
    """Service to reload the device.

    Arguments:
        reload_command: reload command to be issued. default is "reload"
        dialog: Dialog which include list of Statements for
                additional dialogs prompted by reload command, in-case
                it is not in the current list.
        timeout: Timeout value in sec, Default Value is 300 sec
        reload_creds: name or list of names of credential(s) to use if
                      username or password is prompted for during reload.

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
        self.service_name = 'reload'
        self.timeout = connection.settings.RELOAD_TIMEOUT
        self.dialog = Dialog(reload_statement_list)
        self.__dict__.update(kwargs)

    def call_service(self,
                     reload_command='reload',
                     dialog=Dialog([]),
                     target='active',
                     timeout=None,
                     reload_creds=None,
                     *args, **kwargs):
        con = self.connection
        self.context = con.active.context
        timeout = timeout or self.timeout

        fmt_msg = "+++ reloading  %s  " \
                  " with reload_command %s " \
                  "and timeout is %s +++"
        con.log.debug(fmt_msg % (self.connection.hostname,
                                 reload_command,
                                 timeout))

        con.active.state_machine.go_to(self.start_state,
                                con.active.spawn,
                                prompt_recovery=self.prompt_recovery,
                                context=self.context)

        if not isinstance(dialog, Dialog):
            raise SubCommandFailure(
                "dialog passed must be an instance of Dialog")

        show_terminal = con.execute('show terminal')
        line_type = re.search(r"Line .*, Type \"(\w+)\"", show_terminal)
        if line_type and line_type.groups():
            line_type = line_type.group(1)

        if reload_creds:
            context = self.context.copy()
            context.update(cred_list=reload_creds)
        else:
            context = self.context

        if line_type == 'Console':
            dialog += self.dialog
            con.active.spawn.sendline(reload_command)
            try:
                try:
                    self.result = dialog.process(con.active.spawn,
                                   timeout=timeout,
                                   prompt_recovery=self.prompt_recovery,
                                   context=context)
                    if self.result:
                        self.result = self.result.match_output
                except Exception:
                    self.result = con.active.spawn.buffer
                    if 'is in standby' in self.result:
                        con.log.info('Timed out due to active/standby interchanged. Reconnecting...')
                    else:
                        con.log.info('Timed out. timeout might need to be increased. Reconnecting...')
                    con.disconnect()
                    original_connection_timeout = con.settings.CONNECTION_TIMEOUT
                    con.settings.CONNECTION_TIMEOUT = timeout
                    con.connect()
                    con.settings.CONNECTION_TIMEOUT = original_connection_timeout

                con.active.state_machine.go_to('any',
                                        con.active.spawn,
                                        prompt_recovery=self.prompt_recovery,
                                        context=self.context)
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
                            context=context,
                            timeout=standby_wait_interval,
                            prompt_recovery=self.prompt_recovery,
                            dialog=con.connection_provider.get_connection_dialog()
                        )
                        break
                    except Exception as err:
                        if round == standby_sync_try - 1:
                            raise Exception(
                                'Bringing standby to any state failed within {} sec'
                                    .format(standby_wait_time)) from err
            except Exception as err:
                raise SubCommandFailure("Reload failed %s" % err)

            output = self.result
            output = output.replace(reload_command, "", 1)
            # only strip first newline and leave formatting intact
            output = re.sub(r"^\r?\r\n", "", output, 1)
            output = output.rstrip()
        else:
            raise Exception("Console is not used.")

        self.result = output
