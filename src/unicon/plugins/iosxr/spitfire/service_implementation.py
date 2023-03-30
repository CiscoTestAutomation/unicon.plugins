__copyright__ = "# Copyright (c) 2019 by cisco Systems, Inc. All rights reserved."
__author__ = "skanakad"

import io
import re
import logging
import contextlib
import collections
from time import sleep

from unicon.bases.routers.services import BaseService
from unicon.core.errors import SubCommandFailure, TimeoutError
from unicon.eal.dialogs import Dialog
from unicon.plugins.generic.service_implementation import BashService as GenericBashService

from .service_statements import reload_statement_list, reload_statement_list_vty
from .statements import SpitfireStatements

from unicon.logs import UniconStreamHandler, UNICON_LOG_FORMAT

statements = SpitfireStatements()
ReloadResult = collections.namedtuple('ReloadResult', ['result', 'output'])


class Switchto(BaseService):
    """ Switch to a certain CLI state
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.context = context

    def log_service_call(self):
        pass

    def pre_service(self, target_state, *args, **kwargs):

        if not self.connection.is_connected:
            self.connection.log.warning(
                'Device is not connected, ignoring switchto')
            return

        if self.get_sm().current_state == target_state:
            self.connection.log.info(
                f"Device already at the target state {target_state}")
            return
        self.connection.log.info(
            f"+++ {self.service_name}: {target_state} +++")

    def call_service(self, target_state, timeout=None, *args, **kwargs):

        if not self.connection.is_connected:
            return

        con = self.get_handle()
        sm = self.get_sm()

        login_dialog = Dialog([
            statements.bmc_login_stmt, statements.password_stmt,
            statements.login_stmt
        ])
        timeout = timeout if timeout is not None else self.timeout

        valid_states = [x.name for x in sm.states]
        if target_state not in valid_states:
            con.log.warning(
                f'{target_state} is not a valid state, ignoring switchto')
            return

        if sm.current_state == 'xr_env':
            con.sendline('exit')
            con.state_machine.go_to(['xr_bash', 'xr_run'],
                                    con.spawn,
                                    context=self.context,
                                    hop_wise=False,
                                    timeout=timeout,
                                    dialog=login_dialog)

        con.state_machine.go_to(target_state,
                                con.spawn,
                                context=self.context,
                                hop_wise=True,
                                timeout=timeout,
                                dialog=login_dialog)

        self.end_state = sm.current_state

    def post_service(self, *args, **kwargs):
        pass


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
        self.service_name = 'reload'
        self.timeout = connection.settings.RELOAD_TIMEOUT
        self.dialog = Dialog(reload_statement_list)

        self.log_buffer = io.StringIO()
        lb = UniconStreamHandler(self.log_buffer)
        lb.setFormatter(logging.Formatter(fmt=UNICON_LOG_FORMAT))
        self.connection.log.addHandler(lb)

        self.__dict__.update(kwargs)

    def call_service(self,
                     reload_command='reload',
                     dialog=Dialog([]),
                     timeout=None,
                     return_output=False,
                     reload_creds=None,
                     *args,
                     **kwargs):
        con = self.connection
        timeout = timeout or self.timeout
        self.result = False

        # Clear log buffer
        self.log_buffer.seek(0)
        self.log_buffer.truncate()

        fmt_msg = "+++ reloading  %s  " \
                  " with reload_command %s " \
                  "and timeout is %s +++"
        con.log.debug(fmt_msg %
                      (self.connection.hostname, reload_command, timeout))

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
                dialog.process(con.spawn,
                               timeout=timeout,
                               prompt_recovery=self.prompt_recovery,
                               context=context)
                con.state_machine.go_to('any',
                                        con.spawn,
                                        prompt_recovery=self.prompt_recovery,
                                        context=self.context)
            except Exception as err:
                raise SubCommandFailure(f"Reload failed {err}") from err

            self.result = True

        else:
            con.log.warning(
                'Did not detect a console session, will try to reconnect...')
            dialog = Dialog(reload_statement_list_vty)
            con.spawn.sendline(reload_command)
            output = ""
            dialog.process(con.spawn,
                           timeout=timeout,
                           prompt_recovery=self.prompt_recovery,
                           context=self.context)

            con.log.warning('Disconnecting...')
            con.disconnect()
            for x in range(con.settings.RELOAD_ATTEMPTS):
                con.log.warning(
                    f'Waiting for {con.settings.RELOAD_WAIT} seconds')
                sleep(con.settings.RELOAD_WAIT)
                con.log.warning(f'Trying to connect... attempt #{x + 1}')
                try:
                    con.connect()
                    self.result = True
                except Exception:
                    con.log.warning('Connection failed')
                    self.result = False
                if con.is_connected:
                    break

            if not con.is_connected:
                raise SubCommandFailure('Reload failed - could not reconnect')

            self.result = True

        self.log_buffer.seek(0)
        reload_output = self.log_buffer.read()
        # clear buffer
        self.log_buffer.truncate()

        if return_output:
            self.result = ReloadResult(self.result, reload_output)


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
        self.service_name = 'reload'
        self.timeout = connection.settings.RELOAD_TIMEOUT
        self.dialog = Dialog(reload_statement_list)

        self.log_buffer = io.StringIO()
        lb = UniconStreamHandler(self.log_buffer)
        lb.setFormatter(logging.Formatter(fmt=UNICON_LOG_FORMAT))
        self.connection.log.addHandler(lb)

        self.__dict__.update(kwargs)

    def call_service(self,
                     reload_command='reload',
                     dialog=Dialog([]),
                     target='active',
                     timeout=None,
                     return_output=False,
                     reload_creds=None,
                     *args,
                     **kwargs):
        con = self.connection
        timeout = timeout or self.timeout
        self.result = False

        # Clear log buffer
        self.log_buffer.seek(0)
        self.log_buffer.truncate()

        fmt_msg = "+++ reloading  %s  " \
                  " with reload_command %s " \
                  "and timeout is %s +++"
        con.log.debug(fmt_msg %
                      (self.connection.hostname, reload_command, timeout))

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
            line_type = line_type[1]

        if reload_creds:
            context = self.context.copy()
            context.update(cred_list=reload_creds)
        else:
            context = self.context

        if line_type != 'Console':
            raise Exception("Console is not used.")

        dialog += self.dialog
        con.active.spawn.sendline(reload_command)
        try:
            try:
                self.result = dialog.process(
                    con.active.spawn,
                    timeout=timeout,
                    prompt_recovery=self.prompt_recovery,
                    context=context)
                if self.result:
                    reload_output = self.result.match_output
            except Exception:
                reload_output = con.active.spawn.buffer
                if 'is in standby' in reload_output:
                    con.log.info(
                        'Timed out due to active/standby interchanged. Reconnecting...'
                    )
                else:
                    con.log.info(
                        'Timed out. timeout might need to be increased. Reconnecting...'
                    )
                con.disconnect()
                original_connection_timeout = con.settings.CONNECTION_TIMEOUT
                con.settings.CONNECTION_TIMEOUT = timeout
                con.connect()
                con.settings.CONNECTION_TIMEOUT = original_connection_timeout

            con.active.state_machine.go_to(
                'any',
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
                        dialog=con.connection_provider.get_connection_dialog())
                    self.result = True
                    break
                except Exception as err:
                    if round == standby_sync_try - 1:
                        raise Exception(
                            f'Bringing standby to any state failed within {standby_wait_time} sec'
                        ) from err

        except Exception as err:
            raise SubCommandFailure(f"Reload failed {err}") from err

        self.log_buffer.seek(0)
        reload_output = self.log_buffer.read()
        # clear buffer
        self.log_buffer.truncate()

        if return_output:
            self.result = ReloadResult(self.result, reload_output)
        else:
            self.result = reload_output


class BashService(GenericBashService):

    class ContextMgr(GenericBashService.ContextMgr):

        def __enter__(self):
            self.conn.log.debug('+++ attaching bash shell +++')
            sm = self.conn.state_machine
            sm.go_to('xr_run', self.conn.spawn)
            return self
