__author__ = "dwapstra"

import re
from time import sleep
from unicon.eal.dialogs import Dialog
from unicon.core.errors import SubCommandFailure
from unicon.bases.routers.services import BaseService
from unicon.plugins.generic import GenericUtils
from unicon.plugins.generic.service_implementation import Execute as GenericExecute

from .patterns import AciPatterns
from .service_patterns import AciN9kReloadPatterns
from .service_statements import reload_statement_list

utils = GenericUtils()
reload_patterns = AciN9kReloadPatterns()


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



class Reload(BaseService):

    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
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
                     discovery_timeout=0,
                     *args,
                     **kwargs):

        con = self.connection
        timeout = timeout or self.timeout

        fmt_msg = "+++ reloading %s " \
                  "with reload_command '%s' " \
                  "and timeout %s seconds " \
                  "and discovery_timeout %s seconds +++"
        con.log.info(fmt_msg % (self.connection.hostname,
                                 reload_command,
                                 timeout,
                                 discovery_timeout))

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
            if self.result:
                self.result = self.result.match_output

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
        except Exception as err:
            raise SubCommandFailure("Reload failed %s" % err)

        if isinstance(self.result, str):
            self.result = self.result.replace(reload_command, "", 1)

        if discovery_timeout and con.state_machine.current_state == 'enable':
            con.log.info('Waiting up to %s seconds for discovery to finish' % discovery_timeout)
            con.expect(reload_patterns.discovery_done, timeout=discovery_timeout)
            con.log.info('Discovery done, waiting %s seconds' % con.settings.POST_RELOAD_WAIT)
            sleep(con.settings.POST_RELOAD_WAIT)
            con.state_machine.go_to('any',
                                    con.spawn,
                                    prompt_recovery=self.prompt_recovery,
                                    context=self.context,
                                    dialog=con.connection_provider.get_connection_dialog())
            con.connection_provider.init_handle()

        con.log.info("+++ Reload completed +++")

