""" Stack based IOS-XE/cat9k/c9350 service implementations. """
import io, logging
from time import sleep
from collections import namedtuple
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor, wait as wait_futures, ALL_COMPLETED

from unicon.eal.dialogs import Dialog
from unicon.core.errors import SubCommandFailure
from unicon.bases.routers.services import BaseService

from unicon.logs import UniconStreamHandler, UNICON_LOG_FORMAT

from unicon.plugins.iosxe.stack.utils import StackUtils
from unicon.plugins.generic.statements import custom_auth_statements
from unicon.plugins.iosxe.stack.service_statements import (switch_prompt,
                                                           stack_reload_stmt_list,
                                                           stack_reload_stmt_list_1,
                                                           stack_switchover_stmt_list)

utils = StackUtils()

class C9350StackReload(BaseService):
    """ Service to reload the stack device.

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
        self.log_buffer = io.StringIO()
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

        reload_cmd = reload_command if reload_command is not None else self.reload_command
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
            self.error_pattern += append_error_pattern# Connecting to the log handler to capture the buffer output
        
        lb = UniconStreamHandler(self.log_buffer)
        lb.setFormatter(logging.Formatter(fmt=UNICON_LOG_FORMAT))
        self.connection.log.addHandler(lb)

        # logging the output to subconnections
        for subcon in self.connection.subconnections:
            subcon.log.addHandler(lb)

        # Clear log buffer
        self.log_buffer.seek(0)
        self.log_buffer.truncate()
        # update all subconnection context with image_to_boot
        if image_to_boot:
            for subconn in self.connection.subconnections:
                subconn.context.image_to_boot = image_to_boot
            
            # Update the reload command to use the image_to_boot
            self.context["image_to_boot"] = image_to_boot
            reload_cmd = f"boot {image_to_boot.strip()}"
            
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
        if reload_cmd:
            conn.sendline(reload_cmd)

        conn_list = self.connection.subconnections
        reload_cmd_output = None

        def task(con):
            for _ in range(3):
                # The dialog handles the initial reload interaction for c9350 member consoles.
                # It monitors for the prompt "Press RETURN to get started" and responds by sending a RETURN key. 
                # This action is repeated three times to cover the three subsequent "Press RETURN to get started" prompts on a single console.
                # Once each console has been activated, the dialog concludes.
                reload_cmd_output = reload_dialog.process(con.spawn,
                                                          timeout=timeout,
                                                          prompt_recovery=self.prompt_recovery,
                                                          context=con.context)
                self.result = reload_cmd_output.match_output
                self.get_service_result()

                # If device entered rommon state, break out of the loop
                if 'state' in con.context and con.context.state == 'rommon':
                    con.log.info(f"Device {con.alias} entered rommon state, breaking out of reload dialog loop")
                    break

        futures = []
        executor = ThreadPoolExecutor(max_workers=len(conn_list))
        for con in conn_list:
            futures.append(executor.submit(task, con))

        # Wait for all tasks to complete with timeout handling
        future_results, not_completed = wait_futures(
            futures,
            timeout=timeout,
            return_when=ALL_COMPLETED)

        if not_completed:
            # Cancel any remaining futures
            for future in not_completed:
                future.cancel()
            raise SubCommandFailure('Threading timeout')

        # Process completed futures
        for future in future_results:
            try:
                result = future.result()
                conn.log.info(f"Reload result: {result}")

            except Exception as e:
                raise SubCommandFailure('Error during reload', e) from e

        if 'state' in conn.context and conn.context.state == 'rommon':
            conn.log.info(f"Waiting {self.connection.settings.STACK_ROMMON_SLEEP} seconds for all peers to come to boot state ")
            # If manual boot enabled wait for all peers to come to boot state.
            sleep(self.connection.settings.STACK_ROMMON_SLEEP)

            conn.context.pop('state')

            def boot(con):

                # send boot command for each subconnection
                utils.send_boot_cmd(con, timeout, self.prompt_recovery, reply)

                self.connection.log.info('Processing on rp %s-%s' % (con.hostname, con.alias))
                con.context['post_reload_timeout'] = timedelta(seconds= self.post_reload_wait_time)
                # process boot up for each subconnection

                utils.boot_process(con, timeout, self.prompt_recovery, reload_dialog)

            futures = []
            executor = ThreadPoolExecutor(max_workers=len(conn_list))

            for con in conn_list:
                futures.append(executor.submit(boot, con))

            # Wait for all tasks to complete with timeout handling
            future_results, not_completed = wait_futures(
                futures,
                timeout=timeout,
                return_when=ALL_COMPLETED)

            if not_completed:
                # Cancel any remaining futures
                for future in not_completed:
                    future.cancel()
                raise SubCommandFailure('Threading timeout')

            # Process completed futures
            for future in future_results:
                try:
                    result = future.result()
                    conn.log.info(f"Reload result: {result}")

                except Exception as e:
                    raise SubCommandFailure('Error during reload', e) from e

            # After boot_process, bring each subconnection to enable state
            conn.log.info("Bringing devices to enable state post rommon boot")
            for con in conn_list:
                try:
                    con.state_machine.go_to('enable', con.spawn, timeout=timeout,
                                            prompt_recovery=self.prompt_recovery,
                                            context=con.context)
                except Exception as e:
                    raise SubCommandFailure('Failed to bring device to enable mode.', e) from e
        else:
            try:
                conn.log.info("Bring device to any state")
                # bring device to enable mode
                conn.state_machine.go_to('any', conn.spawn, timeout=timeout,
                                        prompt_recovery=self.prompt_recovery,
                                        context=conn.context)
                conn.state_machine.go_to('enable', conn.spawn, timeout=timeout,
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

        self.connection.log.info('Disconnecting and reconnecting')
        self.connection.disconnect()
        self.connection.connect()

        self.connection.log.info("+++ Reload Completed Successfully +++")
        
        # Read the log buffer 
        self.log_buffer.seek(0)
        reload_output = self.log_buffer.read()
        # clear buffer
        self.log_buffer.truncate()

        # Remove the handler
        self.connection.log.removeHandler(lb)
        for subcon in self.connection.subconnections:
            subcon.log.removeHandler(lb)
        
        self.result = True

        if return_output:
            Result = namedtuple('Result', ['result', 'output'])
            self.result = Result(self.result, reload_output.replace(reload_cmd, '', 1))
