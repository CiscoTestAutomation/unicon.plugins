""" IOS-XE Quad service implementations. """
from time import sleep, time
from collections import namedtuple

from unicon.eal.dialogs import Dialog
from unicon.core.errors import SubCommandFailure
from unicon.bases.routers.services import BaseService

from unicon.plugins.generic.statements import custom_auth_statements

from .utils import QuadUtils
from .service_statements import quad_switchover_stmt_list, quad_reload_stmt_list

utils = QuadUtils()

class QuadGetRPState(BaseService):
    """ Get Rp state

    Service to get the redundancy state of the device rp.

    Arguments:
        target: Service target, by default active

    Returns:
        Expected return values are ACTIVE, STANDBY, MEMBER, IN_CHASSIS_STANDBY
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

    def pre_service(self, *args, **kwargs):
        if 'target' in kwargs:
            handle = self.get_handle(kwargs['target'])
            if handle.state_machine.current_state == 'rpr':
                return

        super().pre_service(*args, **kwargs)

    def post_service(self, *args, **kwargs):
        if 'target' in kwargs:
            handle = self.get_handle(kwargs['target'])
            if handle.state_machine.current_state == 'rpr':
                return

        super().post_service(*args, **kwargs)

    def call_service(self,
                     target='active',
                     timeout=None,
                     utils=utils,
                     *args,
                     **kwargs):
        """send the command on the right rp and return the output"""
        handle = self.get_handle(target)
        timeout = timeout or self.timeout
        if handle.state_machine.current_state == 'rpr':
            self.result = {'role': 'IN_CHASSIS_STANDBY'}
            return

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


class QuadSwitchover(BaseService):
    """ Quad switchover service

    Service for Quad device switchover.

    Arguments:
        command ('str'): Switchover command to execute,
                         by default "redundancy force-switchover"
        reply ('Dialog'): Extra switchover dialogs, by default None
        timeout ('int'): Switchover timeout value, by default 600 secs
        sync_standby ('bool'): Whether to sync up standby RP, by default True

    Returns:
        result ('bool'): True/False
        raise SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.switchover()
            rtr.switchover(timeout=900)
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.QUAD_SWITCHOVER_TIMEOUT
        self.command = "redundancy force-switchover"
        self.dialog = Dialog(quad_switchover_stmt_list)
        self.__dict__.update(kwargs)

    def call_service(self, command=None,
                     reply=Dialog([]),
                     timeout=None,
                     sync_standby=True,
                     *args, **kwargs):

        self.result = False
        switchover_cmd = command or self.command
        timeout = timeout or self.timeout
        conn = self.connection.active

        dialog = self.dialog

        if reply:
            dialog = reply + self.dialog
        custom_auth_stmt = custom_auth_statements(
                                conn.settings.LOGIN_PROMPT,
                                conn.settings.PASSWORD_PROMPT)
        if custom_auth_stmt:
            dialog += Dialog(custom_auth_stmt)

        self.connection.log.info('Processing on original Global Active rp '
                                 '%s-%s' % (conn.hostname, conn.alias))
        conn.sendline(switchover_cmd)
        try:
            active_output = dialog.process(conn.spawn, timeout=timeout,
                                    prompt_recovery=self.prompt_recovery,
                                    context=conn.context)
        except Exception as e:
            raise SubCommandFailure('Error during switchover ', e) from e

        # check if active rp changed to rpr state and update state machine
        if 'state' in conn.context and conn.context.state == 'rpr':
            conn.state_machine.detect_state(conn.spawn)
            conn.context.pop('state')

        self.connection.log.info('Processing on new Global Active rp '
            '%s-%s' % (conn.hostname, self.connection.standby.alias))

        if utils.is_active_ready(self.connection.standby):
            self.connection.log.info('Standby RP changed to active role')
            #  Reassign roles for each rp
            #  standby -> active
            #  active ics -> standby
            #  standby ics -> active ics
            #  active -> standby ics
            self.reassign_roles(conn)
        else:
            raise SubCommandFailure('Failed to bring standby rp to active role')

        if not sync_standby:
            self.connection.log.info("Standby state check disabled on user request")
            self.connection.log.info('Switchover successful')
            self.result = True
        else:
            new_active = self.connection.active
            new_standby = self.connection.standby
            self.connection.log.info('Waiting for new standby RP to be STANDBY HOT')

            start_time = time()
            while (time() - start_time) < timeout:
                if utils.is_peer_standby_hot(new_active):
                    self.connection.log.info('Standby RP is in STANDBY HOT state.')
                    break
                else:
                    self.connection.log.info('Sleeping for %s secs.' % \
                        self.connection.settings.QUAD_SWITCHOVER_SLEEP)
                    sleep(self.connection.settings.QUAD_SWITCHOVER_SLEEP)
            else:
                self.connection.log.info('Timeout in %s secs. '
                    'Standby RP is not in STANDBY HOT state. Switchover failed' % timeout)
                self.result = False
                return

            new_active.execute('show module')

            self.connection.log.info('Processing on new Global Standby rp '
                                     '%s-%s' % (conn.hostname, new_standby.alias))
            new_standby.spawn.sendline()
            try:
                new_standby.state_machine.go_to(
                    'any', new_standby.spawn, context=new_standby.context)
                new_standby.state_machine.detect_state(new_standby.spawn)
                new_standby.enable()
            except Exception as e:
                raise SubCommandFailure('Error while bringing standby rp '
                                        'to enable state', e) from e

            self.connection.log.info('Switchover sucessful')
            self.result = True


    def reassign_roles(self, active_con):
        ''' reassign roles for each rp
            standby -> active, active ics -> standby,
            standby ics -> active ics, active -> standby ics
        '''
        self.connection.log.info("Reassign roles for each rp")
        self.connection._set_active_alias(self.connection.standby.alias)
        self.connection._set_standby_alias(self.connection.active_ics.alias)
        self.connection._set_active_ics_alias(self.connection.standby_ics.alias)
        self.connection._set_standby_ics_alias(active_con.alias)

    def post_service(self, *args, **kwargs):
        pass


class QuadReload(BaseService):
    """ Service to reload the Quad device.

    Arguments:
        reload_command: reload command to be used. default "redundancy reload shelf"
        reply: Additional Dialog( i.e patterns) to be handled
        timeout: Timeout value in sec, Default Value is 60 sec
        image_to_boot: image to boot from rommon state
        return_output: if True, return namedtuple with result and reload output

    Returns:
        console True on Success, raises SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.reload()
            # If reload command is other than 'reload'
            rtr.reload(reload_command="reload location all", timeout=700)
    """

    def __init__(self, connection, context, *args, **kwargs):
        super().__init__(connection, context, *args, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.QUAD_RELOAD_TIMEOUT
        self.reload_command = "reload"
        self.dialog = Dialog(quad_reload_stmt_list)
        self.__dict__.update(kwargs)

    def call_service(self, 
                     reload_command=None,
                     reply=Dialog([]),
                     timeout=None,
                     return_output=False,
                     *args, **kwargs):

        self.result = False
        reload_cmd = reload_command or self.reload_command
        timeout = timeout or self.timeout
        conn = self.connection.active

        reload_dialog = self.dialog
        if reply:
            reload_dialog = reply + reload_dialog

        custom_auth_stmt = custom_auth_statements(conn.settings.LOGIN_PROMPT,
                                                  conn.settings.PASSWORD_PROMPT)
        if custom_auth_stmt:
            reload_dialog += Dialog(custom_auth_stmt)

        self.connection.log.info('Processing on rp %s-%s' %
                                (conn.hostname, conn.alias))
        conn.sendline(reload_cmd)
        try:
            reload_output = reload_dialog.process(
                conn.spawn, timeout=timeout,
                prompt_recovery=self.prompt_recovery,
                context=conn.context)
        except Exception as e:
            raise SubCommandFailure('Error during reload', e) from e

        try:
            # check other rp if they reach to stable state
            for subconn in self.connection.subconnections:
                if subconn.alias != conn.alias:
                    self.connection.log.info('Processing on rp %s-%s' %
                                            (conn.hostname, subconn.alias))
                    subconn.spawn.sendline()
                    reload_peer_output = reload_dialog.process(
                        subconn.spawn, timeout=timeout,
                        prompt_recovery=self.prompt_recovery,
                        context=subconn.context)
        except Exception as e:
            raise SubCommandFailure('Reload failed.', e) from e

        self.connection.log.info('Sleeping for %s secs.' % \
                self.connection.settings.QUAD_RELOAD_SLEEP)
        sleep(self.connection.settings.QUAD_RELOAD_SLEEP)

        self.connection.log.info('Disconnecting and reconnecting')
        self.connection.disconnect()
        self.connection.connect()

        self.connection.log.info("+++ Reload Completed Successfully +++")
        self.result = True

        if return_output:
            Result = namedtuple('Result', ['result', 'output'])
            self.result = Result(self.result, reload_output.match_output.replace(reload_cmd, '', 1))
