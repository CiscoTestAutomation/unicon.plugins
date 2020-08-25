""" ConfD/CSP services """

__author__ = "Dave Wapstra <dwapstra@cisco.com>"


import re
import collections
from time import sleep

from unicon.bases.routers.services import BaseService
from unicon.core.errors import SubCommandFailure, StateMachineError
from unicon.eal.dialogs import Dialog, Statement

from unicon.plugins.generic.statements import GenericStatements, \
    authentication_statement_list
from unicon.plugins.confd.patterns import ConfdPatterns
from unicon.plugins.generic import GenericUtils

from .service_statements import reload_statement_list, \
    reload_continue_statement_list


utils = GenericUtils()
statements = GenericStatements()


class Reload(BaseService):
    """Service to reload the device.

    Arguments:
        reload_command: reload command to be issued. default is
                        "system reload" on config mode.
        dialog: Dialog which include list of Statements for
                additional dialogs prompted by reload command, in-case
                it is not in the current list.
        timeout: Timeout value in sec, Default value is {} sec

    Returns:
        Console log output of connected via serial console,
        if connected via SSH returns connect log
        raises SubCommandFailure on failure

    Example ::
        .. code-block:: python

                csp.reload()

    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'cisco_exec'
        self.end_state = 'cisco_exec'
        self.timeout = connection.settings.RELOAD_TIMEOUT
        self.__doc__ = self.__doc__.format(connection.settings.RELOAD_TIMEOUT)

    def call_service(self,
                     reload_command='system reboot',
                     dialog=Dialog([]),
                     timeout=None,
                     *args, **kwargs):
        con = self.connection
        timeout = timeout or self.timeout

        fmt_msg = "+++ reloading %s " \
                  " with reload_command '%s' " \
                  "and timeout %s +++"
        con.log.info(fmt_msg % (self.connection.hostname,
                                 reload_command,
                                 timeout))

        if not isinstance(dialog, Dialog):
            raise SubCommandFailure(
                "dialog passed must be an instance of Dialog")

        if self.context.get('console'):
            dialog = self.service_dialog(service_dialog=dialog)
            dialog += Dialog(authentication_statement_list)
            dialog += Dialog(reload_continue_statement_list)
            con.spawn.sendline(reload_command)
            try:
                self.result = dialog.process(con.spawn,
                                           timeout=timeout,
                                           prompt_recovery=self.prompt_recovery,
                                           context=self.context)
            except Exception as err:
                raise SubCommandFailure("Reload failed %s" % err)

            if self.result:
                self.result = utils.remove_ansi_escape_codes(self.result.match_output)
        else:
            con.log.warning('Did not detect a console session, will try to reconnect...')
            dialog = Dialog(reload_statement_list)
            con.spawn.sendline(reload_command)
            dialog.process(con.spawn,
                           timeout=timeout,
                           prompt_recovery=self.prompt_recovery,
                           context=self.context)
            con.expect('.+')
            con.log.warning('Disconnecting...')
            con.disconnect()
            for x in range(3):
                con.log.warning('Waiting for {} seconds'.format(con.settings.RELOAD_WAIT))
                sleep(con.settings.RELOAD_WAIT)
                con.log.warning('Trying to connect... attempt #{}'.format(x+1))
                try:
                    output = con.connect()
                    self.result = output
                except:
                    con.log.warning('Connection failed')
                if con.connected:
                    break

            if not con.connected:
                raise SubCommandFailure('Reload failed - could not reconnect')
