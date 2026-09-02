__author__ = "dwapstra"

import io
import re
import time
import logging

from unicon.bases.routers.services import BaseService
from unicon.core.errors import SubCommandFailure
from unicon.eal.dialogs import Dialog, Statement
from unicon.logs import UniconStreamHandler, UNICON_LOG_FORMAT

from unicon.plugins.generic.service_implementation import (
    Execute, Switchto as GenericSwitchto
)
from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.generic import GenericUtils

from .statements import (
    FxosStatements, reload_statements,
    login_statements, boot_wait)
from .patterns import FxosPatterns

utils = GenericUtils()
fxos_statements = FxosStatements()
fxos_patterns = FxosPatterns()
generic_statements = GenericStatements()


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
            m1 = re.match(r'module(\s+(\d+))?(\s+(console|telnet))?', to_state)
            m2 = re.match(r'cimc(\s+(\S+))?', to_state)
            m3 = re.match(r'fxos[ _]scope ?(.*)', to_state)
            m4 = re.match(r'adapter(\s+(\S+))?', to_state)
            if m1:
                mod = m1.group(2) or 1
                con_type = m1.group(4) or 'console'
                self.context._module = mod
                self.context._mod_con_type = con_type
                to_state = 'module'
            elif m2:
                mod = m2.group(2) or '1/1'
                self.context._cimc_module = mod
                to_state = 'cimc'
                con.state_machine.go_to('fxos', con.spawn,
                                        context=self.context,
                                        hop_wise=True,
                                        timeout=timeout)
            elif m3:
                scope = m3.group(1)
                if not scope:
                    con.log.warning('No scope specified, ignoring switchto')
                    continue
                else:
                    self.context._scope = scope
                    to_state = 'fxos_scope'
                    con.state_machine.go_to('fxos', con.spawn,
                                            context=self.context,
                                            hop_wise=True,
                                            timeout=timeout)
            elif m4:
                mod = m4.group(2) or '1/1'
                self.context._adapter_module = mod
                to_state = 'adapter'
            else:
                to_state = to_state.replace(' ', '_')

            valid_states = [x.name for x in sm.states]
            if to_state not in valid_states:
                con.log.warning(
                    '%s is not a valid state, ignoring switchto' % to_state)
                continue

            con.state_machine.go_to(to_state,
                                    con.spawn,
                                    context=self.context,
                                    hop_wise=True,
                                    timeout=timeout,
                                    dialog=dialog)

        self.end_state = sm.current_state


class FxosExecute(Execute):
    def log_service_call(self):
        self.connection.log.info('+++ {}: {} +++'.format(
            self.connection.hostname, self.service_name))


class FTD(FxosExecute):
    """ Brings device to the FTD Prompt and execute any commands specified
    """
    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'ftd'
        self.end_state = 'ftd'
        self.service_name = 'ftd'
        self.timeout = 120
        self.__dict__.update(kwargs)


class FireOS(FTD):
    def call_service(self, *args, **kwargs):
        self.connection.log.warning('**** "fireos" service is deprecated. ' +
                                    'Please use "ftd" service ****')
        super().call_service(*args, **kwargs)


class FXOS(FxosExecute):
    """ Brings device to the FXOS Prompt and execute any commands specified
    """
    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'fxos'
        self.end_state = 'fxos'
        self.service_name = 'fxos'
        self.timeout = 120
        self.__dict__.update(kwargs)


class Expert(FxosExecute):
    """ Brings device to the FireOS Expert Prompt and execute any commands specified
    """
    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'expert'
        self.end_state = 'expert'
        self.service_name = 'expert'
        self.timeout = 60
        self.__dict__.update(kwargs)


class Sudo(FxosExecute):
    """ Brings device to the FireOS Sudo Prompt and execute any commands specified
    """
    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'sudo'
        self.end_state = 'sudo'
        self.service_name = 'sudo'
        self.timeout = 60
        self.__dict__.update(kwargs)


class Disable(FxosExecute):
    """ Brings device to the Lina Disable prompt and executes command specified
    """
    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'disable'
        self.end_state = 'disable'
        self.service_name = 'disable'
        self.timeout = 60
        self.__dict__.update(kwargs)


class Enable(FxosExecute):
    """ Brings device to the Lina Enable prompt and executes commands specified
    """
    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.service_name = 'enable'
        self.timeout = 60
        self.__dict__.update(kwargs)


class Rommon(FxosExecute):
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


class FXOSManagement(FxosExecute):
    """ Brings device to the FXOS mgmt prompt and executes commands specified
    """
    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'fxos_mgmt'
        self.end_state = 'fxos_mgmt'
        self.service_name = 'fxos_mgmt'
        self.timeout = 60
        self.__dict__.update(kwargs)


class Reload(BaseService):
    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'fxos'  # start in fxos and switch to ftd in pre_service for console detection and reboot
        self.end_state = 'fxos'
        self.service_name = 'reload'
        self.timeout = self.connection.settings.BOOT_TIMEOUT
        self.log_buffer = io.StringIO()
        lb = UniconStreamHandler(self.log_buffer)
        lb.setFormatter(logging.Formatter(fmt=UNICON_LOG_FORMAT))
        self.connection.log.addHandler(lb)
        self.dialog = Dialog(reload_statements)
        self.__dict__.update(kwargs)

    def pre_service(self, *args, **kwargs):
        super().pre_service(*args, **kwargs)
        # Force switch to ftd so we can detect if we are on console or not and execute the reboot command
        self.connection.ftd()

    def call_service(self, reload_command='reboot', reply=Dialog([]), timeout=None, *args, **kwargs):  # noqa C901
        # Clear log buffer
        self.log_buffer.seek(0)
        self.log_buffer.truncate()

        con = self.connection
        timeout = timeout or self.timeout
        con.log.debug("+++ reloading  %s  with reload_command %s "
                      "and timeout is %s +++" % (self.connection.hostname, reload_command, timeout))

        console = con.context.get('console', False)

        if console:
            dialog = reply + self.dialog
            con.spawn.sendline(reload_command)
            try:
                con.log.info('Rebooting system..')
                # reload and wait until 'Restarting system' is seen
                self.result = dialog.process(con.spawn,
                                             timeout=timeout,
                                             prompt_recovery=self.prompt_recovery,
                                             context=self.context)

                con.log.info('Waiting for boot to finish..')
                # Wait until boot is done
                boot_wait(con.spawn, timeout=timeout or self.timeout)

                con.log.info('Reload done, waiting %s seconds' % con.settings.POST_RELOAD_WAIT)
                time.sleep(con.settings.POST_RELOAD_WAIT)

                dialog = Dialog(login_statements + [Statement(fxos_patterns.fxos_prompt)])

                con.log.info('Trying to login..')
                # try to login
                con.spawn.sendline()
                self.result = dialog.process(con.spawn,
                                             timeout=timeout or self.timeout,
                                             prompt_recovery=self.prompt_recovery,
                                             context=self.context)

                con.state_machine.detect_state(con.spawn)
            except Exception as err:
                raise SubCommandFailure("Reload failed %s" % err)
        else:
            con.log.debug('Did not detect a console session, will try to reconnect...')
            dialog = reply + self.dialog
            con.spawn.sendline(reload_command)
            self.result = dialog.process(con.spawn,
                                         timeout=timeout or self.timeout,
                                         prompt_recovery=self.prompt_recovery,
                                         context=self.context)
            try:
                con.spawn.expect('.+', timeout=10, log_timeout=False)
            except TimeoutError:
                pass
            con.log.info('Disconnecting...')
            con.disconnect()
            for x in range(con.settings.RELOAD_RECONNECT_ATTEMPTS):
                con.log.info('Waiting for {} seconds'.format(con.settings.RELOAD_WAIT))
                time.sleep(con.settings.RELOAD_WAIT)
                con.log.info('Trying to connect... attempt #{}'.format(x + 1))
                try:
                    con.connect()
                except Exception:
                    con.log.warning('Connection failed')
                if con.is_connected:
                    break

            if not con.is_connected:
                raise SubCommandFailure('Reload failed - could not reconnect')

        self.log_buffer.seek(0)
        self.result = self.log_buffer.read()
