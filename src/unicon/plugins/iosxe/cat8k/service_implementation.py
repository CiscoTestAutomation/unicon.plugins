__author__ = "Lukas McClelland <lumcclel@cisco.com>"


import re
import warnings
from time import sleep
from unicon.eal.dialogs import Dialog
from unicon.core.errors import SubCommandFailure
from unicon.bases.routers.services import BaseService
from unicon.plugins.iosxe.cat8k.service_statements import switchover_statement_list


class SwitchoverService(BaseService):
    """ Service to switchover the device.

    Arguments:
        command: command to do switchover. default
                 "redundancy force-switchover"
        dialog: Dialog which include list of Statements for
                additional dialogs prompted by switchover command,
                in-case it is not in the current list.
        timeout: Timeout value in sec, Default Value is 500 sec

    Returns:
        True on Success, raise SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.switchover()
            # If switchover command is other than 'redundancy force-switchover'
            rtr.switchover(command="command to invoke switchover",timeout=700)
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.SWITCHOVER_TIMEOUT
        self.dialog = Dialog(switchover_statement_list)
        self.command = 'redundancy force-switchover'
        self.__dict__.update(kwargs)

    def call_service(self, command=None,
                     reply=Dialog([]),
                     timeout=None,
                     sync_standby=True,
                     *args,
                     **kwargs):

        # create an alias for connection.
        con = self.connection
        timeout = timeout or self.timeout
        command = command or self.command
        reply += self.dialog

        con.log.debug("+++ Issuing switchover on  %s  with "
                      "switchover_command %s and timeout is %s +++"
                      % (con.hostname, command, timeout))

        # Check if switchover is possible by checking if "IOSXE_DUAL_IOS = 1" is
        # in the output of 'sh romvar'
        output = con.execute('show romvar')
        if not re.search('IOSXE_DUAL_IOS\s*=\s*1', output):
            raise SubCommandFailure(
                "Switchover can't be issued if IOSXE_DUAL_IOS is not activated")


        # Issue switchover command
        con.spawn.sendline(command)
        try:
            reply.process(con.spawn,
                           timeout=timeout,
                           prompt_recovery=self.prompt_recovery)
        except TimeoutError:
            pass
        except SubCommandFailure as err:
            raise SubCommandFailure("Switchover Failed %s" % str(err)) from err

        con.state_machine.go_to(
            'any',
            con.spawn,
            prompt_recovery=self.prompt_recovery,
            timeout=con.connection_timeout,
        )
        con.state_machine.go_to(
            'enable',
            con.spawn,
            prompt_recovery=self.prompt_recovery
        )

        if not sync_standby:
            con.log.info("Standby state check disabled on user request")
        else:
            con.log.info('Waiting for standby sync to finish')
            standby_wait_time = con.settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT
            switchover_intervals = con.settings.SWITCHOVER_COUNTER
            sleep_per_interval = standby_wait_time // switchover_intervals + 1
            for interval in range(switchover_intervals):
                try:
                    output = con.execute('show platform')
                except (SubCommandFailure, TimeoutError):
                    con.log.info(
                        "Encountered subcommand failure while trying to "
                        "execute 'show platform'. Waiting for %s seconds"
                        % sleep_per_interval)
                    sleep(sleep_per_interval)
                    continue
                else:
                    if not re.search('R\d+/\d+\s+init,\s*standby.*', output):
                        break
                    elif interval * sleep_per_interval < standby_wait_time:
                        con.log.info(
                            'Standby still initializing. Waiting for %s seconds'
                            % sleep_per_interval)
                        sleep(sleep_per_interval)

                if interval * sleep_per_interval >= standby_wait_time:
                    raise Exception(
                            'Standby failed to complete initialization within '
                            '{} seconds'.format(standby_wait_time))