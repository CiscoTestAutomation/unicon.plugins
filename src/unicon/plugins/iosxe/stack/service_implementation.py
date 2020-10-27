""" Stack based IOS-XE service implementations. """
from time import sleep, time
from collections import namedtuple

from unicon.eal.dialogs import Dialog
from unicon.core.errors import SubCommandFailure
from unicon.bases.routers.services import BaseService

from .utils import StackUtils
from unicon.plugins.generic.statements import custom_auth_statements
from .service_statements import (switch_prompt,
                                 stack_reload_stmt_list,
                                 stack_switchover_stmt_list)

utils = StackUtils()

class StackGetRPState(BaseService):
    """ Get Rp state

    Service to get the redundancy state of the device rp.

    Arguments:
        target: Service target, by default active

    Returns:
        Expected return values are ACTIVE, STANDBY, MEMBER
        raise SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.get_rp_state()
            rtr.get_rp_state(target='standby')
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.__dict__.update(kwargs)

    def call_service(self,
                     target='active',
                     timeout=None,
                     utils=utils,
                     *args,
                     **kwargs):
        """send the command on the right rp and return the output"""
        handle = self.get_handle(target)
        timeout = timeout or self.timeout
        try:
            info_dict = utils.get_redundancy_details(handle, timeout=timeout)
        except Exception as err:
            raise SubCommandFailure("get_rp_state failed", err) from err

        self.result = info_dict.get(str(handle.member_id))

    def get_service_result(self):
        if 'role' in self.result:
            return self.result['role'].upper()
        else:
            return "None"


class StackSwitchover(BaseService):
    """ Get Rp state

    Service to get the redundancy state of the device rp.

    Arguments:
        target: Service target, by default active

    Returns:
        Expected return values are ACTIVE, STANDBY, MEMBER
        raise SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.get_rp_state()
            rtr.get_rp_state(target='standby')
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.STACK_SWITCHOVER_TIMEOUT
        self.command = "redundancy force-switchover"
        self.dialog = Dialog(stack_switchover_stmt_list)
        self.__dict__.update(kwargs)

    def call_service(self, command=None,
                     reply=Dialog([]),
                     timeout=None,
                     *args, **kwargs):

        switchover_cmd = command or self.command
        timeout = timeout or self.timeout
        conn = self.connection.active

        expected_active_sw = self.connection.standby.member_id
        dialog = self.dialog

        if reply:
            dialog = reply + self.dialog

        # added connection dialog in case switchover ask for username/password
        connect_dialog = self.connection.connection_provider.get_connection_dialog()
        dialog += connect_dialog

        conn.sendline(switchover_cmd)
        try:
            match_object = dialog.process(conn.spawn, timeout=timeout,
                            prompt_recovery=self.prompt_recovery,
                            context=conn.context)
        except Exception as e:
            raise SubCommandFailure('Error during switchover ', e) from e

        # try boot up original active rp with current active system 
        # image, if it moved to rommon state.
        if 'state' in conn.context and conn.context.state == 'rommon':
            try:
                conn.state_machine.detect_state(conn.spawn)
                conn.state_machine.go_to('enable', conn.spawn, timeout=timeout,
                            prompt_recovery=self.prompt_recovery,
                            context=conn.context, dialog=Dialog([switch_prompt]))
            except Exception as e:
                self.connection.log.warning('Fail to bring up original active rp from rommon state.', e)
            finally:
                conn.context.pop('state')

        # check all members are ready
        conn.state_machine.detect_state(conn.spawn)

        interval = self.connection.settings.SWITCHOVER_POSTCHECK_INTERVAL
        if utils.is_all_member_ready(conn, timeout=timeout, interval=interval):
            self.connection.log.info('All members are ready.')
        else:
            self.connection.log.info('Timeout in %s secs. '
                'Not all members are in Ready state.' % timeout)
            self.result = False
            return

        self.connection.log.info('Disconnecting and reconnecting')
        self.connection.disconnect()
        self.connection.connect()

        self.connection.log.info('Verifying active and standby switch State.')
        if self.connection.active.member_id == expected_active_sw:
            self.connection.log.info('Switchover successful')
            self.result = True
        else:
            self.connection.log.info('Switchover failed')
            self.result = False


class StackReload(BaseService):
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
        self.dialog = Dialog(stack_reload_stmt_list)

    def call_service(self, 
                     reload_command=None,
                     reply=Dialog([]),
                     timeout=None,
                     image_to_boot=None,
                     return_output=False,
                     *args, **kwargs):

        self.result = False
        reload_cmd = reload_command or self.reload_command
        timeout = timeout or self.timeout
        conn = self.connection.active

        # update all subconnection context with image_to_boot
        if image_to_boot:
            for subconn in self.connection:
                subconn.context.image_to_boot = image_to_boot

        reload_dialog = self.dialog
        if reply:
            reload_dialog = reply + reload_dialog

        custom_auth_stmt = custom_auth_statements(conn.settings.LOGIN_PROMPT,
                                                  conn.settings.PASSWORD_PROMPT)
        if custom_auth_stmt:
            reload_dialog += Dialog(custom_auth_stmt)

        reload_dialog += Dialog([switch_prompt])

        conn.sendline(reload_cmd)
        try:
            reload_cmd_output = reload_dialog.process(
                conn.spawn, timeout=timeout,
                prompt_recovery=self.prompt_recovery,
                context=conn.context)
        except Exception as e:
            raise SubCommandFailure('Error during reload', e) from e

        if 'state' in conn.context and conn.context.state == 'rommon':
            # If manual boot enabled wait for all peers to come to boot state.
            sleep(self.connection.settings.STACK_ROMMON_SLEEP)

            conn.context.pop('state')
            try:
                # send boot command for each subconnection
                for subconn in self.connection.subconnections:
                    utils.send_boot_cmd(subconn, timeout, self.prompt_recovery, reply)

                # process boot up for each subconnection
                for subconn in self.connection.subconnections:
                    self.connection.log.info('Processing on rp '
                        '%s-%s' % (conn.hostname, subconn.alias))
                    utils.boot_process(subconn, timeout, self.prompt_recovery, reload_dialog)

            except Exception as e:
                self.connection.log.error(e)
                raise SubCommandFailure('Reload failed.', e) from e
        else:
            try:
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

        self.connection.log.info('Sleeping for %s secs.' % \
                self.connection.settings.STACK_POST_RELOAD_SLEEP)
        sleep(self.connection.settings.STACK_POST_RELOAD_SLEEP)

        self.connection.log.info('Disconnecting and reconnecting')
        self.connection.disconnect()
        self.connection.connect()

        self.connection.log.info("+++ Reload Completed Successfully +++")
        self.result = True

        if return_output:
            Result = namedtuple('Result', ['result', 'output'])
            self.result = Result(self.result, reload_cmd_output.match_output.replace(reload_cmd, '', 1))
