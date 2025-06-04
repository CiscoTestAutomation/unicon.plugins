""" Stack based IOS-XE/cat9k/c9500X service implementations. """
from time import sleep
from collections import namedtuple
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor, wait as wait_futures, ALL_COMPLETED

from unicon.eal.dialogs import Dialog
from unicon.core.errors import SubCommandFailure
from unicon.bases.routers.services import BaseService

from unicon.plugins.iosxe.stack.utils import StackUtils
from unicon.plugins.generic.statements import custom_auth_statements
from unicon.plugins.iosxe.stack.service_statements import (switch_prompt,
                                                           stack_reload_stmt_list)

utils = StackUtils()


class SVLStackReload(BaseService):
    """ Service to reload the SVL stack device.

    Arguments:
        reload_command: reload command to be used. default "redundancy reload shelf"
        reply: Additional Dialog( i.e patterns) to be handled
        timeout: Timeout value in sec, Default Value is 900 sec
        image_to_boot: image to boot from rommon state
        return_output: if True, return namedtuple with result and reload output

    Returns:
        console True on Success, raises SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.reload()
            # If reload command is other than 'redundancy reload shelf'
            rtr.reload(reload_command="reload location all", timeout=700)
    """

    def __init__(self, connection, context, *args, **kwargs):
        super().__init__(connection, context, *args, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.STACK_RELOAD_TIMEOUT
        self.reload_command = "redundancy reload shelf"
        self.dialog = Dialog(stack_reload_stmt_list)

    def call_service(self,
                     reload_command=None,
                     reply=Dialog([]),
                     timeout=None,
                     image_to_boot=None,
                     return_output=False,
                     member=None,
                     error_pattern = None,
                     append_error_pattern= None,
                     post_reload_wait_time=None,
                     *args,
                     **kwargs):

        self.result = False
        if member:
            reload_command = f'reload slot {member}'
        reload_cmd = reload_command or self.reload_command
        timeout = timeout or self.timeout
        conn = self.connection.active

        if error_pattern is None:
            self.error_pattern = self.connection.settings.ERROR_PATTERN
        else:
            self.error_pattern = error_pattern

        if post_reload_wait_time is None:
            self.post_reload_wait_time = self.connection.settings.POST_RELOAD_WAIT
        else:
            self.post_reload_wait_time = post_reload_wait_time

        if not isinstance(self.error_pattern, list):
            raise ValueError('error_pattern should be a list')
        if append_error_pattern:
            if not isinstance(append_error_pattern, list):
                raise ValueError('append_error_pattern should be a list')
            self.error_pattern += append_error_pattern
        # update all subconnection context with image_to_boot
        if image_to_boot:
            for subconn in self.connection.subconnections:
                subconn.context.image_to_boot = image_to_boot
        reload_dialog = self.dialog
        if reply:
            reload_dialog = reply + reload_dialog

        custom_auth_stmt = custom_auth_statements(conn.settings.LOGIN_PROMPT,
                                                  conn.settings.PASSWORD_PROMPT)
        if custom_auth_stmt:
            reload_dialog += Dialog(custom_auth_stmt)

        reload_dialog += Dialog([switch_prompt])

        conn.context['post_reload_wait_time'] = timedelta(seconds= self.post_reload_wait_time)

        conn.log.info('Processing on active rp %s-%s with timeout %s' % (conn.hostname, conn.alias, timeout))
        conn.sendline(reload_cmd)

        conn_list = self.connection.subconnections
        reload_cmd_output = None

        def task(con):

            # The following multithreading logic is designed to manage
            # all the subconnections within the stack.
            # A loop has been implemented to handle the
            # "Press RETURN to get started" prompt twice. Based on extensive
            # testing during SVL reloads on 9500x devices, it was observed
            # that the device is not fully ready after the first prompt.
            # As a result, the logic accounts for this behavior by waiting for
            # the second occurrence of the message, which is assumed to be the
            # default behavior for these devices.

            for _ in range(2):
                reload_cmd_output = reload_dialog.process(con.spawn,
                                                          timeout=timeout,
                                                          prompt_recovery=self.prompt_recovery,
                                                          context=con.context)
                self.result = reload_cmd_output.match_output
                self.get_service_result()

        futures = []
        executor = ThreadPoolExecutor(max_workers=len(conn_list))

        for con in conn_list:
            futures.append(executor.submit(task, con))

        # Log the output from threading
        future_results = wait_futures(futures, timeout=timeout, return_when=ALL_COMPLETED)

        # Splitting it to done and not done specifically
        # because future result is a tuple

        # Logs the completed output
        done = list(future_results.done)

        # Logs the error traceback
        not_done = list(future_results.not_done)

        for future in done + not_done:
            try:
                result = future.result()
                conn.log.info(f"Reload result: {result}")
            except Exception as e:
                raise SubCommandFailure('Error during reload', e) from e

        if 'state' in conn.context and conn.context.state == 'rommon':
            conn.log.info(f"Waiting {self.connection.settings.STACK_ROMMON_SLEEP} seconds for all peers to come to boot state")
            # If manual boot enabled wait for all peers to come to boot state.
            sleep(self.connection.settings.STACK_ROMMON_SLEEP)

            conn.context.pop('state')

            def boot(con):

                # send boot command for each subconnection
                utils.send_boot_cmd(con, timeout, self.prompt_recovery, reply)

                self.connection.log.info('Processing on rp %s-%s' % (con.hostname, con.alias))
                con.context['post_reload_timeout'] = timedelta(seconds= self.post_reload_wait_time)

                # process boot up for each subconnection
                # The following multithreading logic is designed to manage
                # all the subconnections within the stack.
                # A loop has been implemented to handle the
                # "Press RETURN to get started" prompt twice. Based on extensive
                # testing during SVL reloads on 9500x devices, it was observed
                # that the device is not fully ready after the first prompt.
                # As a result, the logic accounts for this behavior by waiting for
                # the second occurrence of the message, which is assumed to be the
                # default behavior for these devices.
                for _ in range(2):
                    utils.boot_process(con, timeout, self.prompt_recovery, reload_dialog)

            futures = []
            executor = ThreadPoolExecutor(max_workers=len(conn_list))

            for con in conn_list:
                futures.append(executor.submit(boot, con))

            # Log the output from threading
            future_results = wait_futures(futures, timeout=timeout, return_when=ALL_COMPLETED)

            # Splitting it to done and not done specifically
            # because future result is a tuple

            # Logs the completed output
            done = list(future_results.done)

            # Logs the error traceback
            not_done = list(future_results.not_done)

            for future in done + not_done:
                try:
                    result = future.result()
                    conn.log.info(f"Reload result: {result}")

                except Exception as e:
                    raise SubCommandFailure('Error during reload', e) from e
        else:
            try:
                # bring device to enable mode
                conn.sendline()
                conn.log.info("Bringing device to any state")
                conn.state_machine.go_to('any', conn.spawn, timeout=timeout,
                                        prompt_recovery=self.prompt_recovery,
                                        context=conn.context)

            except Exception as e:
                raise SubCommandFailure('Failed to bring device to disable mode.', e) from e

        # check active and standby rp is ready
        self.connection.log.info('Wait for Standby RP to be ready.')
        interval = self.connection.settings.RELOAD_POSTCHECK_INTERVAL
        if utils.is_active_standby_ready(conn, timeout=timeout, interval=interval):
            self.connection.log.info('Active and Standby RPs are ready.')
        else:
            self.connection.log.info('Timeout in %s secs. '
                'Standby RP is not in Ready state. Reload failed' % timeout)
            self.result = False
            return

        if member:
            if utils.is_all_member_ready(conn, timeout=timeout, interval=interval):
                self.connection.log.info('All Members are ready.')
            else:
                self.connection.log.info(f'Timeout in {timeout} secs. '
                    f'Member{member} is not in Ready state. Reload failed')
                self.result = False
                return

        self.connection.log.info('Sleeping for %s secs.' % \
                self.connection.settings.STACK_POST_RELOAD_SLEEP)
        sleep(self.connection.settings.STACK_POST_RELOAD_SLEEP)

        self.connection.log.info('Initialize the connection after reload')
        self.connection.connection_provider.init_connection()

        self.connection.log.info("+++ Reload Completed Successfully +++")
        self.result = True

        if return_output:
            Result = namedtuple('Result', ['result', 'output'])
            self.result = Result(self.result, reload_cmd_output.match_output.replace(reload_cmd, '', 1))
