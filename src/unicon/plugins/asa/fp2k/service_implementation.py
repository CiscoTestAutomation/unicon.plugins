import io
import re
import time
import logging

from unicon.eal.dialogs import Dialog
from unicon.bases.routers.services import BaseService
from unicon.logs import UniconStreamHandler, UNICON_LOG_FORMAT

from unicon.plugins.fxos.statements import FxosStatements
from unicon.plugins.generic.service_implementation import Switchto as GenericSwitchto

from .statements import reload_statements

fxos_statements = FxosStatements()


class Switchto(GenericSwitchto):
    """ Switch to a certain CLI state
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)

    def call_service(self, to_state,
                     timeout=None,
                     *args, **kwargs):

        if not self.connection.connected:
            return

        con = self.connection
        sm = self.get_sm()

        dialog = Dialog([fxos_statements.command_not_completed_stmt])

        timeout = timeout if timeout is not None else self.timeout

        if isinstance(to_state, str):
            to_state_list = [to_state]
        elif isinstance(to_state, list):
            to_state_list = to_state
        else:
            raise Exception('Invalid switchto to_state type: %s' % repr(to_state))

        for to_state in to_state_list:
            m1 = re.match(r'fxos scope (.*)', to_state)
            m2 = re.match(r'fxos (admin|root)', to_state)
            if m1:
                scope = m1.group(1)
                self.context._scope = scope
                to_state = 'fxos_scope'
                con.state_machine.go_to('fxos', con.spawn,
                                        context=self.context,
                                        hop_wise=True,
                                        timeout=timeout)
            elif m2:
                con_mode = m2.group(1).strip()
                if con_mode == 'admin':
                    to_state = 'fxos'
                    self.context._fxos_connect_mode = con_mode
                elif con_mode == 'root':
                    to_state = 'sudo'
                    self.context._fxos_connect_mode = ''
                else:
                    con.log.warning('%s is not a valid fxos connect mode, ignoring switchto' % con_mode)
                    self.context._fxos_connect_mode = ''
                    return
            else:
                to_state = to_state.replace(' ', '_')

            valid_states = [x.name for x in sm.states]
            if to_state not in valid_states:
                con.log.warning('%s is not a valid state, ignoring switchto' % to_state)
                return

            con.state_machine.go_to(to_state,
                                    con.spawn,
                                    context=self.context,
                                    hop_wise=True,
                                    timeout=timeout,
                                    dialog=dialog)

        self.end_state = sm.current_state


class Reload(BaseService):
    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.service_name = 'reload'
        self.timeout = self.connection.settings.BOOT_TIMEOUT
        self.log_buffer = io.StringIO()
        lb = UniconStreamHandler(self.log_buffer)
        lb.setFormatter(logging.Formatter(fmt=UNICON_LOG_FORMAT))
        self.connection.log.addHandler(lb)
        self.dialog = Dialog(reload_statements)
        self.__dict__.update(kwargs)

    def call_service(self, reload_command='reload', reply=Dialog([]), timeout=None, *args, **kwargs):
        # Clear log buffer
        self.log_buffer.seek(0)
        self.log_buffer.truncate()

        con = self.connection
        timeout = timeout or self.timeout
        con.log.debug("+++ reloading  %s  with reload_command %s "
                      "and timeout is %s +++" % (self.connection.hostname, reload_command, timeout))

        dialog = reply + self.dialog
        con.spawn.sendline(reload_command)
        self.result = dialog.process(con.spawn,
                                     timeout=timeout or self.timeout,
                                     prompt_recovery=self.prompt_recovery,
                                     context=self.context)

        console = con.context.get('console', False)
        if not console:
            con.log.debug('Did not detect a console session, will try to reconnect...')
            try:
                con.spawn.expect('.+', timeout=10, log_timeout=False)
            except TimeoutError:
                pass
            con.log.info('Disconnecting...')
            con.disconnect()
            for x in range(con.settings.RELOAD_RECONNECT_ATTEMPTS):
                con.log.info('Waiting for {} seconds'.format(con.settings.RELOAD_WAIT))
                time.sleep(con.settings.RELOAD_WAIT / (x + 1))
                con.log.info('Trying to connect... attempt #{}'.format(x + 1))
                try:
                    con.connect()
                except Exception:
                    con.log.warning('Connection failed')
                if con.is_connected:
                    break

        if not con.is_connected:
            return False, 'Reload failed - could not reconnect'
        else:
            self.log_buffer.seek(0)
            output = self.log_buffer.read()
            return True, output

