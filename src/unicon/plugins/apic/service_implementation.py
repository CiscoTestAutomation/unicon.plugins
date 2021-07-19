__author__ = "dwapstra"

import io
import re
import logging
from time import sleep
from unicon.logs import UniconStreamHandler, UNICON_LOG_FORMAT
from unicon.bases.routers.services import BaseService
from unicon.plugins.generic.service_implementation import Execute as GenericExecute
from unicon.plugins.generic import GenericUtils
from unicon.core.errors import SubCommandFailure
from unicon.eal.dialogs import Dialog

from .service_statements import reload_statement_list

utils = GenericUtils()


class Execute(GenericExecute):
    """ Execute Service implementation

    Service  to executes exec_commands on the device and return the
    console output. reply option can be passed for the interactive exec
    command.

    Arguments:
        command: exec command
        reply: Additional Dialog patterns for interactive exec commands.
        timeout : Timeout value in sec, Default Value is 60 sec
        lines: number of lines to capture when paging is active. Default: 100

    Returns:
        True on Success, raise SubCommandFailure on failure

    Example:
        .. code-block:: python

              output = dev.execute("show command")

    """

    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)

    def post_service(self, *args, clean_output=True, **kwargs):
        super().post_service(*args, **kwargs)

        if clean_output:
            if isinstance(self.result, str):
                output = self.result
                output = utils.remove_ansi_escape_codes(output)
                output = re.sub('.\x08', '', output)
                output = re.sub(r'%\s+\r ', '', output)
                self.result = output


class Reload(BaseService):

    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.RELOAD_TIMEOUT
        self.dialog = Dialog(reload_statement_list)
        self.log_buffer = io.StringIO()
        lb = UniconStreamHandler(self.log_buffer)
        lb.setFormatter(logging.Formatter(fmt=UNICON_LOG_FORMAT))
        self.connection.log.addHandler(lb)
        self.__dict__.update(kwargs)

    def call_service(self,
                     reload_command='acidiag reboot',
                     dialog=Dialog([]),
                     timeout=None,
                     *args,
                     **kwargs):

        # Clear log buffer
        self.log_buffer.seek(0)
        self.log_buffer.truncate()

        con = self.connection
        timeout = timeout or self.timeout

        fmt_msg = "+++ reloading %s " \
                  "with reload_command '%s' " \
                  "and timeout %s seconds +++"
        con.log.info(fmt_msg % (self.connection.hostname,
                                reload_command,
                                timeout))

        con.state_machine.go_to(self.start_state,
                                con.spawn,
                                prompt_recovery=self.prompt_recovery,
                                context=self.context)

        if not isinstance(dialog, Dialog):
            raise SubCommandFailure(
                "dialog passed must be an instance of Dialog")

        dialog += self.dialog
        con.spawn.sendline(reload_command)
        try:
            self.result = dialog.process(con.spawn,
                                         timeout=timeout,
                                         prompt_recovery=self.prompt_recovery,
                                         context=self.context)
        except Exception as err:
            raise SubCommandFailure("Reload failed\n"
                                    "Error: {}\n"
                                    "Buffer: {}".format(err, repr(con.spawn.buffer)))

        if self.result:
            self.result = self.result.match_output

        if self.context.get('console'):
            con.log.info('Reload done, waiting %s seconds' % con.settings.POST_RELOAD_WAIT)
            sleep(con.settings.POST_RELOAD_WAIT)

            con.sendline()

            con.state_machine.go_to('any',
                                    con.spawn,
                                    prompt_recovery=self.prompt_recovery,
                                    context=self.context,
                                    timeout=con.connection_timeout,
                                    dialog=con.connection_provider.get_connection_dialog())

            if con.state_machine.current_state == 'enable':
                con.connection_provider.init_handle()
        else:
            con.log.debug('Did not detect a console session, will try to reconnect...')
            con.log.info('Disconnecting...')
            con.disconnect()

            reload_wait = con.settings.POST_RELOAD_WAIT
            for x in range(con.settings.RELOAD_RECONNECT_ATTEMPTS):
                con.log.info('Waiting for {} seconds'.format(reload_wait / (x + 1)))
                sleep(reload_wait / (x + 1))
                con.log.info('Trying to connect... attempt #{}'.format(x + 1))
                try:
                    con.connect()
                except Exception:
                    con.log.warning('Connection failed')
                if con.is_connected:
                    break

            if not con.is_connected:
                raise SubCommandFailure('Reload failed - could not reconnect')

        con.log.info("+++ Reload completed +++")

        self.log_buffer.seek(0)
        self.result = self.log_buffer.read()
