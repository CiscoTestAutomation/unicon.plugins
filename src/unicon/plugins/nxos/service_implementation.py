"""
Module:
    unicon.plugins.generic

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    This subpackage implements services specific to NXOS

"""

import re
import collections
import warnings

from time import sleep

from unicon.bases.routers.services import BaseService
from unicon.plugins.generic.service_implementation import (
    BashService as GenericBashService)
from unicon.core.errors import (SubCommandFailure, TimeoutError,
    UniconAuthenticationError)

from unicon.eal.dialogs import Dialog, Statement
from unicon.plugins.generic.service_implementation import \
    Execute as GenericExecute
from unicon.plugins.generic.service_implementation import \
    Copy as GenericCopy, ReloadResult
from unicon.plugins.generic.service_implementation import \
    HAReloadService as GenericHAReload
from unicon.plugins.generic.service_implementation import \
    Reload as GenericReload
from unicon.plugins.generic.service_implementation import \
    GetMode as GenericGetMode
from unicon.plugins.generic.service_implementation import \
    GetRPState as GenericGetRPState
from unicon.plugins.generic.service_implementation import \
    SwitchoverService as GenericSwitchover
from unicon.plugins.generic.service_implementation import \
    Configure as GenericConfigure
from unicon.plugins.generic.service_statements import ping6_statement_list, \
    switchover_statement_list, standby_reset_rp_statement_list
from unicon.plugins.generic.service_statements import send_response
from unicon.plugins.nxos.service_statements import nxos_reload_statement_list, \
    ha_nxos_reload_statement_list, execute_stmt_list
from unicon.settings import Settings
from unicon.utils import (AttributeDict, pyats_credentials_available,
    to_plaintext)
from .patterns import NxosPatterns

from .utils import NxosUtils

from .service_statements import config_commit_stmt_list

import unicon.plugins.nxos

patterns = NxosPatterns()
settings = Settings()
utils = NxosUtils()


class NxosCopy(GenericCopy):
    """ Implements Copy service for NXOS

    Service to support nxos  copy command, which basically
    copies images and configs into and out of router Flash memory.

    Arguments:
        source: filename/device partition/remote type.
        dest: destination filename/device partition/remote type.
        source_file: source file name in device disk/tftp.
        dest_file: destination file name on device disk/tftp (file name with path).
        server: tftp/ftp server address.
        vrf: VRF interface name.
        timeout: Timeout value in sec.

    Returns:
        True on Success, raise SubCommandFailure on failure
    """
    def call_service(self, *args, **kwargs):
        if 'dest_file' in kwargs and 'dest' in kwargs:
            if re.match(self.copy_pat.remote_in_dest, kwargs['dest'].strip()):
                if 'server' in kwargs:
                    kwargs['dest'] = kwargs['dest'] + '//' + kwargs['server'] + \
                                     '/' +kwargs['dest_file']
            elif re.match(r'.*:/*$', kwargs['dest'].strip()):
                kwargs['dest'] = kwargs['dest'] + '/' +kwargs['dest_file']
        super().call_service(*args, **kwargs)


class Configure(GenericConfigure):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'config'
        self.end_state = 'enable'
        self.mode = 'default'
        self.valid_transition_commands = ['end', 'exit']

    def pre_service(self, *args, **kwargs):
        target = kwargs.get('target', None)
        handle = self.get_handle(target)
        mode = kwargs.get('mode') or self.mode
        if mode == 'dual':
            self.commit_cmd = 'commit'
            handle.context['config_dual'] = True
        try:
            super().pre_service(*args, **kwargs)
        except Exception:
            raise
        finally:
            handle.context.pop('config_dual', None)

    def call_service(self, command=[], reply=Dialog([]),
                     timeout=None, commit=False, *args, **kwargs):
        if commit:
            self.commit_cmd = 'commit'
            self.valid_transition_commands = ['end', 'exit', 'commit', 'abort']

            commit_verification_stmt = Statement(pattern=r'.*{hostname}#.*'.format(
                hostname = self.context['hostname']),
                action=None,
                args=None, loop_continue=False,
                continue_timer=False)

            super().call_service(command,
                                 reply=reply + Dialog([commit_verification_stmt]),
                                 timeout=timeout, *args, **kwargs)

        else:
            super().call_service(command,
                                 reply=reply,
                                 timeout=timeout, *args, **kwargs)

    def post_service(self, *args, **kwargs):
        self.commit_cmd = ''
        super().post_service(*args, **kwargs)


class ConfigureDual(Configure):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.commit_cmd = 'commit'

    def pre_service(self, *args, **kwargs):
        warnings.warn(message = "service 'configure_dual' "
            "is now deprecated and replaced by configure(mode='dual').",
            category = DeprecationWarning)

        target = kwargs.get('target', None)
        handle = self.get_handle(target)
        handle.context['config_dual'] = True
        try:
            super().pre_service(*args, **kwargs)
        except Exception:
            raise
        finally:
            handle.context.pop('config_dual', None)


class Reload(GenericReload):
    """ Service to reload the device.

    Arguments:
        reload_command: reload command to be issued on device.
            default reload_command is "reload"
        dialog: Dialog which include list of Statements for
            additional dialogs prompted by reload command, in-case
            it is not in the current list.
        timeout: Timeout value in sec, Default Value is 400 sec
        return_output: if True, return namedtuple with result and reload output
        config_lock_retries: retry times if config mode is locked, default is 20
        config_lock_retry_sleep: sleep between retries, default is 9 sec
        reload_creds: name or list of names of credential(s) to use if
                      username or password is prompted for during reload.

    Returns:
        bool: True on success False otherwise

    Raises:
        SubCommandFailure: on failure.

    Example:
        .. code-block:: python

            rtr.reload()
            # If reload command is other than 'reload'
            rtr.reload(reload_command="reload location all", timeout=400)
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.dialog = Dialog(nxos_reload_statement_list)
        self.timeout = connection.settings.RELOAD_TIMEOUT
        self.command = 'reload'
        self.__dict__.update(kwargs)

    def call_service(self,
                     reload_command='reload',
                     dialog=Dialog([]),
                     timeout=None,
                     return_output=False,
                     config_lock_retries=None,
                     config_lock_retry_sleep=None,
                     reload_creds=None,
                     reconnect_sleep=None,
                     *args, **kwargs):
        con = self.connection
        timeout = timeout or self.timeout
        reconnect_sleep = reconnect_sleep or con.settings.RELOAD_RECONNECT_WAIT
        config_lock_retries = config_lock_retries \
                              or con.settings.CONFIG_POST_RELOAD_MAX_RETRIES
        config_lock_retry_sleep = config_lock_retry_sleep \
                                  or con.settings.CONFIG_POST_RELOAD_RETRY_DELAY_SEC
        con.log.debug("+++ reloading  %s  with reload_command %s "
                      "and timeout is %s +++"
                      % (self.connection.hostname, reload_command, timeout))
        con.state_machine.go_to(self.end_state,
                                con.spawn,
                                prompt_recovery=self.prompt_recovery,
                                context=self.context)
        if not isinstance(dialog, Dialog):
            raise SubCommandFailure(
                "dialog passed must be an instance of Dialog")
        dialog = self.service_dialog(service_dialog=dialog)
        dialog += self.dialog
        con.spawn.sendline(reload_command)

        if reload_creds:
            context = self.context.copy()
            context.update(cred_list=reload_creds)
        else:
            context = self.context

        try:
            reload_output=dialog.process(con.spawn,
                           context=context,
                           prompt_recovery=self.prompt_recovery,
                           timeout=timeout)
            counter = 3
            while(counter < 3):
                counter = counter + 1
                try:
                    con.state_machine.go_to('any',
                                            con.spawn,
                                            prompt_recovery=self.prompt_recovery,
                                            context=self.context)
                    break
                except Exception as err:
                    if counter >= 3:
                        raise Exception(' Bringing device failed even after retries') from err
                    con.log.info('Retry in process')
                    con.spawn.sendline()
        except Exception as err:
            raise SubCommandFailure("Reload failed : %s" % err)

        con.log.info("Disconnecting")
        con.disconnect()

        con.log.info("Sleeping for %s secs before reconnect" % reconnect_sleep)
        sleep(reconnect_sleep)

        learn_hostname_ori = con.learn_hostname
        # During initialization after reload, hostname may temporarily be "switch".
        # When initialization finishes, hostname will be back to original hostname.
        con.learn_hostname = False
        config_lock_retries_ori = con.settings.CONFIG_LOCK_RETRIES
        con.configure.lock_retries = config_lock_retries
        config_lock_retry_sleep_ori = con.settings.CONFIG_LOCK_RETRY_SLEEP
        con.configure.lock_retry_sleep = config_lock_retry_sleep

        try:
            con.connect()
        finally:
            con.learn_hostname = learn_hostname_ori
            con.settings.CONFIG_LOCK_RETRIES = config_lock_retries_ori
            con.settings.CONFIG_LOCK_RETRY_SLEEP = config_lock_retry_sleep_ori

        con.log.debug("+++ Reload Completed Successfully +++")
        self.result = True
        if return_output:
            self.result = ReloadResult(self.result, reload_output.match_output.replace(reload_command, '', 1))


class Ping6(BaseService):
    """
      Generic ping6 subcommand

    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = 60
        self.dialog = Dialog(ping6_statement_list)
        self.result = None

        # Ping error Patterns
        self.error_pattern = ['^.*(% )?DSCP.*does not match any topology',
                              'Bad IP (A|a)ddress', 'Ping transmit failed',
                              'Invalid vrf', 'Unable to find',
                              'No Route to Host.*',
                              'Destination Host Unreachable',
                              'Unable to initialize Windows Socket Interface',
                              'IP routing table .* does not exist',
                              'Invalid input',
                              'bad context', 'Failed to resolve',
                              '(U|u)nknown (H|h)ost',
                              'Success rate is 0 percent',
                              '100.00% packet loss',
                              '100 % packat loss']

        # add the keyword arguments to the object
        self.__dict__.update(kwargs)

    def call_service(self, *args, **kwargs):
        con = self.get_handle()

        # Ping Options
        ping_options = ['multicast', 'transport', 'mask', 'vcid', 'tunnel',
                        'dest_start', 'dest_end', 'exp', 'pad', 'ttl',
                        'reply_mode', 'dscp', 'proto', 'count', 'size',
                        'verbose', 'interval', 'timeout_limit',
                        'send_interval', 'vrf', 'src_route_type',
                        'src_route_addr', 'extended_verbose', 'topo',
                        'validate_reply_data', 'force_exp_null_label',
                        'lsp_ping_trace_rev', 'oif', 'tos', 'data_pat',
                        'int', 'udp', 'precedence', 'novell_type',
                        'extended_timeout_limit', 'sweep_min', 'sweep_max',
                        'sweep_interval', 'src_addr', 'df_bit',
                        'ipv6_ext_headers', 'ipv6_hbh_headers',
                        'ipv6_dst_headers', 'ping_packet_timeout',
                        'sweep_ping', 'timestamp_count', 'record_hops',
                        'ping_failures', 'extd_ping', 'addr'
                        ]

        # Default value setting
        ping_context = AttributeDict({})
        for a in ping_options:
            if a == "novell_type":
                ping_context[a] = "\r"
            elif a == "sweep_ping":
                ping_context[a] = "n"
            elif a == 'extd_ping':
                ping_context[a] = "n"
            else:
                ping_context[a] = ""

        # Read input values passed
        # Stringify values in case they are passed as objects.
        for key in kwargs:
            ping_context[key] = str(kwargs[key])

        # Validate Inputs
        if ping_context['addr'] == "":
            if args[0]:
                # Stringify address in case it is passed as an object.
                ping_context['addr'] = str(args[0])
            else:
                raise SubCommandFailure("Address is not specified ")

        if ping_context['src_route_type'] != "":
            if ping_context['src_route_addr'] in "":
                raise SubCommandFailure(
                    "If src route type is set, then src route addr is mandatory \n")
        elif ping_context['src_route_addr'] != "":
            raise SubCommandFailure(
                "If src route addr is set, then src route type is mandatory \n")

        timeout = self.timeout
        ping_str = 'ping6' + " " + ping_context['addr']

        # Arguments that need to pass to ping6 command on device.
        # Sequence matters for ping6 command.
        # Key is unicon ping6 service arguments.
        # Value is device ping6 arguments. Prepend and append whitespace.
        ping_seq = collections.OrderedDict()
        ping_seq['multicast'] = ' multicast '
        ping_seq['int'] = ' interface '
        ping_seq['src_addr'] = ' source '
        ping_seq['count'] = ' count '
        ping_seq['send_interval'] = ' interval '
        ping_seq['size'] = ' packet-size '
        ping_seq['vrf'] = ' vrf '

        for unicon_arg, ping6_arg in ping_seq.items():
            if ping_context[unicon_arg]:
                ping_str = ping_str + ping6_arg + ping_context[unicon_arg]

        dialog = self.service_dialog(service_dialog=self.dialog)

        con.spawn.sendline(ping_str)
        try:
            self.result = dialog.process(con.spawn,
                                         context=ping_context,
                                         timeout=timeout)
        except Exception as err:
            raise SubCommandFailure("Ping6 failed", err)
        con.state_machine.go_to(self.end_state, con.spawn,
                                context=self.context)
        self.result = self.result.match_output
        if self.result.rfind(self.connection.hostname):
            self.result = self.result[
                          :self.result.rfind(self.connection.hostname)]


class GetRPState(GenericGetRPState):
    """ Get Rp state

    Service to get the redundancy state of the device rp.
    Returns  standby rp state if standby is passed as input.

    Arguments:
        target: Service target, by default active

    Returns:
        Expected return values are ACTIVE, STANDBY COLD, STANDBY HOT
        raise SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.get_rp_state()
            rtr.get_rp_state(target='standby')
    """
    def call_service(self,
                     target='active',
                     timeout=None,
                     utils=utils,
                     *args,
                     **kwargs):

        """send the command on the right rp and return the output"""
        super().call_service(
            target = target,
            timeout = timeout,
            utils = utils,
            *args,
            **kwargs)

class GetMode(GenericGetMode):
    """ Service to get the redundancy mode of the device.

    Returns:
        'sso', 'rpr' or raise SubCommandFailure on failure.

    Example ::
        .. code-block:: python

            rtr.get_mode()
    """

    def call_service(self,
                     target='active',
                     timeout=None,
                     utils=utils,
                     *args,
                     **kwargs):

        super().call_service(
            target = target,
            timeout = timeout,
            utils = utils,
            *args,
            **kwargs)



class HANxosReloadService(GenericHAReload):
    """ Service to reload the device.

    Arguments:
        reload_command : reload command to be issued on device.
        default reload_command is "reload"

        dialog : Dialog which include list of Statements for
                additional dialogs prompted by reload command, in-case
                it is not in the current list.

        timeout : Timeout value in sec, Default Value is 600 sec
        return_output: if True, return namedtuple with result and reload output
        config_lock_retries: retry times if config mode is locked, default is 20
        config_lock_retry_sleep: sleep between retries, default is 9 sec
        reload_creds: name or list of names of credential(s) to use if
                      username or password is prompted for during reload.

    Returns:
        bool: True on success False otherwise

    Raises:
        SubCommandFailure: on failure.

    Example:
        .. code-block:: python

              rtr.reload()
              # If reload command is other than 'reload'
              rtr.reload(reload_command="reload location all", timeout=700)
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.result = None
        self.timeout = connection.settings.HA_RELOAD_TIMEOUT
        self.dialog = Dialog(ha_nxos_reload_statement_list)
        self.command = 'reload'
        self.__dict__.update(kwargs)

    def call_service(self, reload_command='reload',
                     dialog=Dialog([]),
                     target='active',
                     timeout=None,
                     return_output=False,
                     config_lock_retries=None,
                     config_lock_retry_sleep=None,
                     reload_creds=None,
                     *args,
                     **kwargs):

        """send the command on the right rp and return the output"""
        # create an alias for connection.
        con = self.connection
        timeout = timeout or self.timeout
        config_lock_retries = config_lock_retries \
                              or con.settings.CONFIG_POST_RELOAD_MAX_RETRIES
        config_lock_retry_sleep = config_lock_retry_sleep \
                                  or con.settings.CONFIG_POST_RELOAD_RETRY_DELAY_SEC
        # TODO counter value must be defined settings
        counter = 0
        config_retry = 0
        state_machine = self.connection.active.state_machine
        con.log.debug(
            "+++ reloading  %s  with reload_command %s and timeout is %s +++"
            % (con.hostname, reload_command, timeout))

        active_dialog = dialog + self.service_dialog(
            handle=con.active, service_dialog=self.dialog)
        standby_dialog = dialog + self.service_dialog(
            handle=con.standby, service_dialog=self.dialog)

        if reload_creds:
            context = con.active.context.copy()
            context.update(cred_list=reload_creds)
            sby_context = con.standby.context.copy()
            sby_context.update(cred_list=reload_creds)
        else:
            context = con.active.context
            sby_context = con.standby.context

        state_machine.go_to('enable',
                            con.active.spawn,
                            prompt_recovery=self.prompt_recovery,
                            context=self.context)

        # Issue reload command
        con.active.spawn.sendline(reload_command)
        try:
            reload_op = active_dialog.process(
                con.active.spawn,
                context=context,
                prompt_recovery=self.prompt_recovery,
                timeout=timeout
            )
            reload_op_standby=standby_dialog.process(
                con.standby.spawn,
                context=sby_context,
                prompt_recovery=self.prompt_recovery,
                timeout=timeout
            )
            con.log.debug("Waiting for HA Config Sync to complete")
            sleep(con.settings.POST_HA_RELOAD_CONFIG_SYNC_WAIT)

            counter = 0
            while(counter < 3):
                counter = counter + 1
                try:
                    state_machine.go_to('any',
                        con.active.spawn,
                        context=context,
                        timeout=100,
                        prompt_recovery=self.prompt_recovery,
                        dialog=con.connection_provider.get_connection_dialog())
                    break
                except Exception as err:
                    if counter >= 3:
                        raise Exception(' Bringing device failed even after retries') from err
                    con.log.info('Retry in process')

                    con.active.spawn.sendline()
                # con.active.state_machine.go_to('any', con.active.spawn, context=self.context)
            # Bring standby to good state.
            stdby_counter = 0
            while(stdby_counter < 3):
                con.standby.spawn.sendline()
                stdby_counter = stdby_counter + 1
                try:
                    state_machine.go_to('any',
                        con.standby.spawn,
                        context=sby_context,
                        timeout=100,
                        prompt_recovery=self.prompt_recovery,
                        dialog=con.connection_provider.get_connection_dialog())
                    break
                except Exception as err:
                    if stdby_counter >= 3:
                        raise Exception(' Bringing standby to any state failed even after retries') from err
                    con.log.info('Retry in process')
        except Exception as err:
            raise SubCommandFailure("Reload failed : %s" % err)

        # Re-designate handles before applying config.
        self.connection.connection_provider.designate_handles()

        state_machine.go_to('enable',
                            con.active.spawn,
                            prompt_recovery=self.prompt_recovery,
                            context=context)

        # Issue init commands to disable console logging
        exec_commands = self.connection.settings.HA_INIT_EXEC_COMMANDS
        for command in exec_commands:
            con.execute(command)
        config_commands = self.connection.settings.HA_INIT_CONFIG_COMMANDS
        try:
            con.configure(config_commands,
                          prompt_recovery=self.prompt_recovery,
                          lock_retries=config_lock_retries,
                          lock_retry_sleep=config_lock_retry_sleep)
        except:
            pass
        while counter < 31:
            rp_state = con.get_rp_state(target='standby', timeout=30)
            if rp_state.find('STANDBY HOT') != -1:
                counter = 32
            else:
                sleep(6)
                counter += 1
        # Stabilise the standby handle
        con.disconnect()
        sleep(10)
        #Set config retries here and reset back to default.
        learn_hostname_ori = con.learn_hostname
        # During initialization after reload, hostname may temporarily be "switch".
        # When initialization finishes, hostname will be back to original hostname.
        con.learn_hostname = False
        config_lock_retries_ori = con.settings.CONFIG_LOCK_RETRIES
        con.configure.lock_retries = config_lock_retries
        config_lock_retry_sleep_ori = con.settings.CONFIG_LOCK_RETRY_SLEEP
        con.configure.lock_retry_sleep = config_lock_retry_sleep

        try:
            con.connect()
        finally:
            con.learn_hostname = learn_hostname_ori
            con.settings.CONFIG_LOCK_RETRIES = config_lock_retries_ori
            con.settings.CONFIG_LOCK_RETRY_SLEEP = config_lock_retry_sleep_ori

        con.log.debug("+++ Reload Completed Successfully +++")
        self.result = True
        if return_output:
            self.result = ReloadResult(self.result, reload_op.match_output.replace(reload_command, '', 1))


class NxosSwitchoverService(GenericSwitchover):
    """ Service to switchover the device.


        :arg : command : command to be issued on device to switchover.
               default command is "redundancy force-switchover"

               switchover_creds: credential or list of credentials to use to
                        respond to username/password prompts.
               dialog : Dialog which include list of Statements for
                        additional dialogs prompted by switchover command,
                        in-case it is not in the current list.

               timeout : Timeout value in sec, Default Value is 500 sec

        :return : True on Success
                  raise SubCommandFailure on failure.

        Example ::

                  rtr.switchover()

                  # If switchover command is other than 'redundancy force-switchover'
                  rtr.switchover(command="command which invoke switchover",
                             timeout=700)

    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.result = None
        self.timeout = connection.settings.SWITCHOVER_TIMEOUT
        self.dialog = Dialog(switchover_statement_list)
        self.command = 'system switchover'
        self.__dict__.update(kwargs)

    def call_service(self, command='system switchover',
                     reply=Dialog([]),
                     timeout=None,
                     sync_standby=True,
                     switchover_creds=None,
                     *args,
                     **kwargs):
        # create an alias for connection.
        con = self.connection
        timeout = timeout or self.timeout
        switchover_counter = con.settings.SWITCHOVER_COUNTER
        con.log.debug("+++ Issuing switchover on  %s  with "
                      "switchover_command %s and timeout is %s +++"
                      % (con.hostname, command, timeout))

        # Check is switchover possible?
        rp_state = con.get_rp_state(target='standby', timeout=timeout)
        if rp_state.find('STANDBY HOT') == -1:
            raise SubCommandFailure(
                "Switchover can't be issued in %s state" % rp_state)

        # Use the standby credentials when processing because any
        # authentication request is expected to come from the new active.
        if switchover_creds:
            context = con.standby.context.copy()
            context.update(cred_list=switchover_creds)
        else:
            context = con.standby.context

        # Save current active and standby handle details
        standby_start_cmd = con.standby.start
        # Bring Standby to enable state
        con.enable(target='standby')
        dialog = self.service_dialog(handle=con.active,
                                     service_dialog=self.dialog)
        # Issue switchover command
        con.active.spawn.sendline(command)
        try:
            dialog.process(con.active.spawn,
                           context=context,
                           prompt_recovery=self.prompt_recovery,
                           timeout=timeout)
        except TimeoutError:
            pass
        except SubCommandFailure as err:
            raise SubCommandFailure("Switchover Failed %s" % str(err))

        # Initialise Standby
        try:
            con.standby.spawn.sendline("\r")
            con.standby.spawn.expect(".*")
            con.swap_roles()
            con.active.state_machine.go_to('any',
                                           con.active.spawn,
                                           context=context,
                                           timeout=timeout,
                                           prompt_recovery=self.prompt_recovery,
                                           dialog=con.connection_provider.get_connection_dialog())
        except Exception as err:
            raise SubCommandFailure("Failed to initialise the standby",
                                    err)

        if not sync_standby:
            con.log.info("Standby state check disabled on user request")
        else:
            counter = 0
            while counter < switchover_counter:
                con.active.spawn.sendline("\r")
                con.active.spawn.expect(".*")
                try:
                    rp_state = con.get_rp_state(target='standby',
                                                timeout=60)
                except (SubCommandFailure, TimeoutError):
                    sleep(9)
                    counter += 1
                    continue
                except Exception:
                    con.active.spawn.sendline("\r")
                    con.active.spawn.expect(".*")
                    continue
                else:
                    if re.search('STANDBY HOT', rp_state):
                        counter = switchover_counter + 1
                    else:
                        sleep(9)
                        counter += 1

            # Issue init commands to disable console logging
            exec_commands = self.connection.settings.HA_INIT_EXEC_COMMANDS
            for command in exec_commands:
                con.execute(command)
            config_commands = self.connection.settings.HA_INIT_CONFIG_COMMANDS
            config_retry = 0
            while config_retry < 20:
                try:
                    con.configure(
                        config_commands,
                        timeout=60,
                        prompt_recovery=self.prompt_recovery)
                except Exception as err:
                    if re.search("Config mode cannot be entered",
                                 str(err)):
                        sleep(9)
                        con.active.spawn.sendline()
                        config_retry += 1
                else:
                    config_retry = 21

            # Clear Standby buffer
            con.standby.spawn.sendline("\r")
            con.standby.spawn.expect(".*")
            con.disconnect()
            con.connect()
            # Verify switchover is Successful
        if con.active.start == standby_start_cmd:
            con.log.info("Switchover is Successful")
            self.result = True
        else:
            con.log.info("Switchover is Failed")
            self.result = False


class ResetStandbyRP(BaseService):
    """ Service to reset the standby rp.


        :arg : command : command to be issued on device to reset the standby.
               default command is "system standby manual-boot"

               dialog : Dialog which include list of Statements for
                        additional dialogs prompted by standby reset command,
                        in-case it is not in the current list.

               timeout : Timeout value in sec, Default Value is 500 sec

        :return : True on Success
                  raise SubCommandFailure on failure.

        Example ::

                  rtr.reset_standby_rp()

                  # If command is other than 'system standby manual-boot'
                  rtr.reset_standby_rp(command="command which invoke reload on standby-rp",
                             timeout=600)

    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.result = None
        self.timeout = connection.settings.HA_RELOAD_TIMEOUT
        self.dialog = Dialog(standby_reset_rp_statement_list)
        self.command = 'system standby manual-boot'
        self.__dict__.update(kwargs)

    def call_service(self, command='system standby manual-boot',
                     reply=Dialog([]),
                     timeout=None,
                     *args,
                     **kwargs):
        # create an alias for connection.
        con = self.connection
        con.log.warning("reset_standby_rp is not supported on NXOS")
        return


class NxosExecute(GenericExecute):
    """ Service to execute commands on nxos.

    Arguments:
        command: List of command to execute on nxos
        dialog: Dialog which include list of Statements for
                additional dialogs prompted by command executed,
                in-case it is not in the current list.
        timeout: Timeout value in sec for executing command on shell.

    Returns:
        string: console output on success

    Raises:
        SubCommandFailure: on failure.

    Example:
        .. code-block:: python

            dev.execute(cmd)
    """
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog += Dialog(execute_stmt_list)

class ShellExec(BaseService):
    """ Service to execute commands on shell.

    Arguments:
        command: List of command to execute on shell
        dialog: Dialog which include list of Statements for
                additional dialogs prompted by command executed,
                in-case it is not in the current list.
        timeout: Timeout value in sec for executing command on shell.

    Returns:
        string: console output on success

    Raises:
        SubCommandFailure: on failure.

    Example:
        .. code-block:: python

            rtr.shellexec(['uname -a'])
            cmd = ['uname -a', 'ls -l']
            dev.shellexec(cmd)
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'shell'
        self.end_state = 'enable'
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.result = None
        self.__dict__.update(kwargs)

    def call_service(self, command=[],
                     reply=Dialog([]),
                     timeout=None,
                     *args, **kwargs):
        con = self.connection
        timeout = timeout or self.timeout
        self.command_list_is_empty = False
        try:
            con.state_machine.go_to(self.start_state,
                                    con.spawn,
                                    context=self.context)
        except Exception as err:
            raise SubCommandFailure("Failed to bring device to shell State",
                                    err)
        # if commands is a list
        if isinstance(command, collections.abc.Sequence):
            # No command passed, just move to config mode
            if len(command) == 0:
                self.result = " "
                self.command_list_is_empty = True
            elif len(command) == 1:
                dialog = self.service_dialog(service_dialog=reply)
                con.spawn.sendline(command[0])
                try:
                    self.result = dialog.process(con.spawn, timeout=timeout)
                except Exception as err:
                    raise SubCommandFailure(
                        "Failed to execute command on shell", err)
                self.result = self.result.match_output
                if self.result.rfind(self.connection.hostname):
                    self.result = self.result[
                                  :self.result.rfind(self.connection.hostname)]
            else:
                dialog = self.service_dialog(service_dialog=reply)
                # Commands are list of more than one command
                for cmd in command:
                    con.spawn.sendline(cmd)
                    try:
                        self.result = dialog.process(con.spawn,
                                                     context=self.context,
                                                     timeout=timeout)
                    except Exception as err:
                        raise SubCommandFailure(
                            "Failed to execute command on shell", err)
                con.state_machine.go_to(self.end_state, con.spawn,
                                        context=self.context)
                self.result = self.result.match_output
                if self.result.rfind(self.connection.hostname):
                    self.result = self.result[
                                  :self.result.rfind(self.connection.hostname)]
        else:
            dialog = self.service_dialog(service_dialog=reply)
            con.spawn.sendline(command)
            try:
                self.result = dialog.process(con.spawn,
                                             context=self.context,
                                             timeout=timeout)
            except Exception as err:
                raise SubCommandFailure("Failed to execute command on shell",
                                        err)
            con.state_machine.go_to(self.end_state, con.spawn,
                                    context=self.context)
            self.result = self.result.match_output
            if self.result.rfind(self.connection.hostname):
                self.result = self.result[
                              :self.result.rfind(self.connection.hostname)]

    def post_service(self, *args, **kwargs):
        if self.command_list_is_empty:
            pass
        else:
            state_machine = self.connection.state_machine
            state_machine.go_to(self.end_state,
                                self.connection.spawn,
                                context=self.connection.context)


class HAShellExec(BaseService):
    """ Service to execute commands on shell.

    Arguments:
        command: List of command to execute on shell
        dialog: Dialog which include list of Statements for
                additional dialogs prompted by command executed,
                in-case it is not in the current list.
        timeout : Timeout value in sec for executing command on shell.

    Returns:
        console output:  on Success

    Raises:
        SubCommandFailure: on failure.

    Example ::
        .. code-block:: python

            rtr.shellexec(['uname -a'])
            cmd = ['uname -a', 'ls -l']
            dev.shellexec(cmd)
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'shell'
        self.end_state = 'enable'
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.result = None
        # add the keyword arguments to the object
        self.__dict__.update(kwargs)

    def call_service(self, command=[],
                     reply=Dialog([]),
                     timeout=None,
                     target=None,
                     *args, **kwargs):
        con = self.connection
        con.log.debug("+++ shellexec  +++")
        timeout = timeout or self.timeout
        self.command_list_is_empty = False

        spawn = self.get_spawn(target)
        handle = self.get_handle(target)
        state_machine = self.get_sm(target)
        try:
            state_machine.go_to(self.start_state,
                                spawn,
                                context=self.context)
        except Exception as err:
            raise SubCommandFailure("Failed to Bring device to Shell State",
                                    err)

        # if commands is a list
        if isinstance(command, collections.abc.Sequence):
            # No command passed, just move to config mode
            if len(command) == 0:
                self.result = " "
                self.command_list_is_empty = True
            elif len(command) == 1:
                dialog = self.service_dialog(service_dialog=reply,
                                             handle=handle)
                spawn.sendline(command[0])
                try:
                    self.result = dialog.process(spawn, timeout=timeout)
                except Exception as err:
                    raise SubCommandFailure(
                        "Failed to Bring device to shell State", err)
                self.result = self.result.match_output
                if self.result.rfind(self.connection.hostname):
                    self.result = self.result[
                                  :self.result.rfind(self.connection.hostname)]
            else:
                dialog = self.service_dialog(service_dialog=reply,
                                             handle=handle)
                # Commands are list of more than one command
                for cmd in command:
                    spawn.sendline(cmd)
                    try:
                        self.result = dialog.process(spawn, timeout=timeout)
                    except Exception as err:
                        raise SubCommandFailure("Configuration failed", err)
                state_machine.go_to(self.end_state, spawn, context=self.context)
                self.result = self.result.match_output
                if self.result.rfind(self.connection.hostname):
                    self.result = self.result[
                                  :self.result.rfind(self.connection.hostname)]
        else:
            dialog = self.service_dialog(service_dialog=reply, handle=handle)
            spawn.sendline(command)
            try:
                self.result = dialog.process(spawn,
                                             context=self.context,
                                             timeout=timeout)
            except Exception as err:
                raise SubCommandFailure("Configuration failed", err)
            state_machine.go_to(self.end_state, spawn, context=self.context)
            self.result = self.result.match_output
            if self.result.rfind(self.connection.hostname):
                self.result = self.result[
                              :self.result.rfind(self.connection.hostname)]

    def post_service(self, *args, **kwargs):
        if self.command_list_is_empty:
            pass
        else:
            state_machine = self.connection.active.state_machine
            state_machine.go_to(self.end_state,
                                self.connection.active.spawn,
                                context=self.connection.context)


class ListVdc(BaseService):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'

    def call_service(self, timeout=10, command="show vdc"):
        initial_vdc = self.connection.current_vdc
        # in case not on default vdc then switchback
        if initial_vdc:
            self.connection.switchback()
        buffer = self.connection.execute("show vdc", timeout=timeout)
        self.result = re.findall(r'^\d+\s+(\S+)', buffer, re.MULTILINE)
        if initial_vdc:
            self.connection.switchto(initial_vdc)


class SwitchVdc(BaseService):
    """Switch to a given VDC Name

    This command is available on the 'switchto' attribute of the connection
    object. In case the user is already on a VDC, it can switchback to the
    default and again switch to the said vdc, hence this command can be issued
    even from other VDCs

    Arguments:
        vdc_name: name of the vdc to switch to.
        timeout: timeout for the whole operations.
        dialog: additional dialog provided by the user.
        vdc_passwd: required for first login, defaults to tacacs password.
        vdc_cred: credential to use for first login.
        command: alternate command to be used.

    Example:
        .. code-block:: python

            con.switchto("vdc2")

    Raises:
        SubCommandFailure Error
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'

    def call_service(self, vdc_name,
                     timeout=20,
                     command="switchto vdc",
                     dialog=Dialog([]),
                     vdc_cred=None,
                     vdc_passwd=None):

        con = self.connection

        if pyats_credentials_available and vdc_passwd:
            warnings.warn(message = "Argument 'vdc_passwd' "
                "is now deprecated and replaced by 'vdc_cred'.",
                category = DeprecationWarning)

        credentials = con.context.credentials
        if credentials:
            credential = vdc_cred or con.context.default_cred_name
            try:
                vdc_passwd = to_plaintext(credentials[credential]['password'])
            except KeyError:
                raise UniconAuthenticationError("No password found "
                    "for credential {}.".format(credential))
        else:
            vdc_passwd = vdc_passwd or con.context.tacacs_password


        command = command + " " + vdc_name

        # if we are already on the same vdc, just bypass the call
        if con.current_vdc == vdc_name:
            con.log.info("device already on %s" % vdc_name)
            return vdc_name

        # vdc name must be valid one.
        vdc_list = con.list_vdc()
        if vdc_name not in vdc_list:
            raise SubCommandFailure("invalid vdc name: %s" % vdc_name)

        # in case we are on a VDC already, we need to switchback first
        if con.current_vdc is not None and \
                        con.current_vdc != vdc_name:
            con.switchback()

        new_hostname = con.hostname + '-' + vdc_name
        if con.is_ha:
            con.active.state_machine.hostname = new_hostname
            con.standby.state_machine.hostname = new_hostname
        else:
            con.state_machine.hostname = new_hostname

        # prepare the dialog to be used.
        command_dialog = Dialog([
            [patterns.secure_password, send_response, {'response': "yes"}, True, True],
            [patterns.admin_password, send_response, {'response': vdc_passwd}, True, True],
            [patterns.setup_dialog, send_response, {'response': "no"}, True, True],
        ])
        # append the dialog which user has provided.
        command_dialog += dialog
        dialog = self.service_dialog(service_dialog=command_dialog)

        try:
            con.sendline(command)
            self.result = dialog.process(con.spawn,
                                         context=self.context,
                                         timeout=timeout)
        except Exception:
            # this means there was some problem during the switching. Hence
            # rollback all the changes to the state machine
            if con.is_ha:
                con.active.state_machine.hostname = \
                    con.hostname
                con.standby.state_machine.hostname = \
                    con.hostname
            else:
                # update the vdc name in connection
                con.state_machine.hostname = \
                    con.hostname
                SubCommandFailure("failed to switch to vdc %s" % vdc_name)
        else:
            con.current_vdc = vdc_name
            # init the connection after switching into a vdc
            if con.is_ha:
                con.connection_provider.init_active()
            else:
                # duck type this properly in connection class.
                con.connection_provider.init_handle()
            self.result = vdc_name


class SwitchbackVdc(BaseService):
    """switches back to default vdc"""

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'

    def call_service(self, timeout=10, command="switchback", dialog=Dialog()):
        con = self.connection
        # this service should be called only if we are on the VDC
        if con.current_vdc:
            hostname = con.hostname
            if con.is_ha:
                con.active.state_machine.hostname = hostname
                con.standby.state_machine.hostname = hostname
            else:
                con.state_machine.hostname = hostname
            con.current_vdc = None
            con.sendline(command)
            dialog = self.service_dialog(service_dialog=dialog)
            dialog.process(con.spawn,
                           context=self.context,
                           prompt_recovery=self.prompt_recovery,
                           timeout=self.timeout)
        else:
            con.log.info("already on default vdc")


class CreateVdc(BaseService):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'

    def call_service(self, vdc_name, command="vdc", dialog=Dialog(),
                     timeout=120):
        initial_vdc = self.connection.current_vdc
        # Stringify command in case it is passed in as an object.
        command = str(command) + " " + vdc_name
        # the vdc should not be already present
        vdc_list = self.connection.list_vdc()
        if vdc_name in vdc_list:
            raise SubCommandFailure("vdc %s already exists" % vdc_name)

        # if not on default vdc then switchback before creating vdc
        if initial_vdc:
            self.connection.switchback()

        self.connection.configure(command, timeout=timeout, reply=dialog)
        self.result = vdc_name

        # if user was on some vdc when issuing this subcommand then switch
        # him back
        if initial_vdc:
            self.connection.switchto(initial_vdc)


class DeleteVdc(BaseService):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = "enable"
        self.end_state = "enable"

    def call_service(self, vdc_name, command="no vdc", dialog=Dialog(),
                     timeout=90):
        # Stringify the command in case it is passed as an object.
        command = str(command) + " " + vdc_name
        initial_vdc = self.connection.current_vdc

        # cant delete the vdc on which device is present right now.
        if vdc_name == initial_vdc:
            raise SubCommandFailure(
                "can't delete vdc %s because device is already on that vdc"
                % vdc_name)

        # device must be in default vdc
        if initial_vdc:
            self.connection.switchback()

        # vdc must exist before it can be deleted.
        vdc_list = self.connection.list_vdc()
        if vdc_name not in vdc_list:
            raise SubCommandFailure("vdc %s doesn't exist" % vdc_name)

        # form the dialog
        command_dialog = Dialog([
            [patterns.delete_vdc_confirm, send_response, {'response': "yes"},
             True, True]
        ])

        # add user dialog if provided
        command_dialog += dialog
        self.connection.configure(
            command, reply=command_dialog, timeout=timeout)
        self.result = vdc_name

        # if the device was no some vdc while issue this command then change
        # vdc to initial_vdc
        if initial_vdc:
            self.connection.switchto(initial_vdc)


class AttachModuleConsole(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_state = "enable"
        self.end_state = "enable"

    def call_service(self, module_num, **kwargs):
        self.result = self.__class__.ContextMgr(connection=self.connection,
                                                module_num=module_num,
                                                **kwargs)

    class ContextMgr(object):
        def __init__(self,
                     connection,
                     module_num,
                     login_name='root',
                     default_escape_chars='~,',
                     change_prompt='AUT0MAT10N# ',
                     timeout=None):
            self.conn = connection
            self.module_num = module_num
            self.login_name = login_name
            self.escape_chars = default_escape_chars
            self.change_prompt = change_prompt
            self.timeout = timeout or connection.settings.CONSOLE_TIMEOUT

        def __enter__(self):
            self.conn.log.debug('+++ attaching console +++')
            # attach to console
            self.conn.sendline('attach console module %s' % self.module_num)
            try:
                match = self.conn.expect([r"Escape character is "
                                          r"(?P<escape_chars>.+?)'"],
                                          timeout=self.timeout)
            except SubCommandFailure:
                pass
            else:
                # save the new escape chars
                self.escape_chars = match.last_match.groupdict()['escape_chars']

            # slow console
            for _ in range(3):
                try:
                    self.conn.sendline('')
                    self.conn.expect([r'.*login:'], timeout=self.timeout)
                except TimeoutError:
                    pass
                except Exception:
                    # disabled for 5 minutes
                    sleep(self.conn.settings.ATTACH_CONSOLE_DISABLE_SLEEP)
                    self.conn.sendline('')
                    self.conn.expect([r'.*login:'], timeout=self.timeout)
                else:
                    break
            self.conn.sendline(self.login_name)
            self.conn.expect([r'%s@.+?:~#' % self.login_name],
                             timeout=self.timeout)

            # change the prompt and make our life easy
            self.execute("export PS1='%s'" % self.change_prompt)

            return self

        def execute(self, command, timeout=None):
            # take default if not set
            timeout = timeout or self.timeout

            # send the command
            self.conn.sendline(command)

            # expect output until prompt again
            # wait for timeout provided by user
            out = self.conn.expect([r'(.+)[\r\n]*%s' % self.change_prompt],
                                   timeout=timeout)

            raw = out.last_match.groups()[0].strip()

            # remove the echo back - best effort
            # (bash window uses a carriage return + space  to wrap over 80 char)
            if raw.split('\r\n')[0].replace(' \r', '').strip() == command:
                raw = '\r\n'.join(raw.split('\r\n')[1:])

            return raw

        def __exit__(self, exc_type, exc_value, exc_tb):
            self.conn.log.debug('--- detaching console ---')
            # disconnect console
            self.conn.sendline('') # clear last bad command

            # burn the buffer
            self.conn.expect([r'.+'], timeout=self.timeout)

            # get out
            try:
                self.conn.sendline('exit')
                self.conn.expect([r'.*login:'], timeout=self.timeout)
            except Exception:
                sleep(self.conn.settings.ATTACH_CONSOLE_DISABLE_SLEEP)
                self.conn.sendline('exit')
                self.conn.expect([r'.*login:'], timeout=self.timeout)

            self.conn.sendline(self.escape_chars)
            # do not suppress
            return False

        def __getattr__(self, attr):
            if attr in ('sendline', 'send'):
                return getattr(self.conn, attr)

            raise AttributeError('%s object has no attribute %s'
                                 % (self.__class__.__name__, attr))


class BashService(GenericBashService):

    class ContextMgr(GenericBashService.ContextMgr):
        def __init__(self, connection, enable_bash=False, timeout=None):
            # overwrite the prompt
            super().__init__(connection=connection,
                             enable_bash=enable_bash,
                             timeout=timeout)

        def __enter__(self):
            self.conn.log.debug('+++ attaching bash shell +++')
            # overwrite the command to go into the shell
            if self.enable_bash:
                # enable bash feature
                if self.conn.parent:
                    self.conn.parent.active.configure(
                        'feature bash', timeout=self.timeout)
                else:
                    self.conn.configure('feature bash', timeout=self.timeout)

            sm = self.conn.state_machine
            sm.go_to('shell', self.conn.spawn)

            return self


class GuestshellService(BaseService):
    """Service to provide a Linux console.

    Arguments:
        enable_guestshell: Enable the guestshell if not already enabled
        timeout: Timeout for entering/exiting guestshell mode
        retries: If enable_guestshell is True, number of retries
          (waiting 5 seconds per retry) to successfully issue the
          "guestshell enable" command, and also the number of retries to wait
          for the guestshell to become activated afterward.
          Default is 20 (100 seconds maximum)

    Example:
        .. code-block:: python

            with rtr.guestshell(enable_guestshell=True, retries=10) as gs:
                gs.execute("ifconfig")

            with rtr.guestshell() as gs:
                gs.execute("ls")
                gs.execute("pwd")
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_state = "enable"
        self.end_state = "enable"

    def call_service(self, **kwargs):
        self.result = self.__class__.ContextMgr(connection=self.connection,
                                                **kwargs)

    class ContextMgr(object):
        def __init__(self, connection,
                     enable_guestshell=False, timeout=None, retries=None):
            self.conn = connection
            self.enable_guestshell = enable_guestshell
            self.timeout = timeout or connection.settings.EXEC_TIMEOUT
            self.retries = retries or connection.settings.GUESTSHELL_RETRIES

        def __enter__(self):
            if self.enable_guestshell:
                self.conn.log.debug("+++ enabling guestshell +++")
                # "guestshell enable" may fail with a "please retry request"
                # if the guestshell is already undergoing another transition,
                # so we may potentially need to retry the command.
                for i in range(self.retries):
                    # Note: "guestshell enable" is an exec command not a config
                    output = self.conn.execute('guestshell enable',
                                               timeout=self.timeout)
                    if not output.strip():
                        # Command was accepted
                        break
                    elif "already enabled" in output:
                        break
                    elif "please retry request" in output:
                        sleep(self.conn.settings.GUESTSHELL_RETRY_SLEEP)
                        continue
                    else:
                        # Other output indicates some unexpected failure
                        raise SubCommandFailure(
                            "Failed to enable guestshell: %s" % output)
                else:
                    raise SubCommandFailure(
                        "Failed to enable guestshell after %d tries"
                        % self.retries)

                # Okay, we successfully issued "guestshell enable".
                # Now it may take some time for the guestshell to become
                # fully activated (ready for use).
                self.conn.log.debug("+++ waiting for guestshell activation +++")
                for i in range(self.retries):
                    output = self.conn.execute("show guestshell | i State",
                                               timeout=self.timeout)

                    if "activated" in output.lower():
                        # Success
                        break
                    elif "failed" in output.lower():
                        # Terminal state, won't recover
                        raise SubCommandFailure(
                            "Failed to install/activate guestshell: %s"
                            % output)
                    else:
                        # Not yet ready
                        sleep(self.conn.settings.GUESTSHELL_RETRY_SLEEP)
                        continue
                else:
                    raise SubCommandFailure(
                        "Guestshell failed to become activated after %d tries"
                        % self.retries)

            self.conn.log.debug('+++ entering guestshell +++')
            conn = self.conn.active if self.conn.is_ha else self.conn
            conn.state_machine.go_to('guestshell',
                                     conn.spawn,
                                     timeout=self.timeout,
                                     context=self.conn.context)

            return self

        def __exit__(self, *args):
            self.conn.log.debug('--- exiting guestshell ---')
            conn = self.conn.active if self.conn.is_ha else self.conn
            conn.state_machine.go_to('enable',
                                     conn.spawn,
                                     timeout=self.timeout,
                                     context=self.conn.context)

            # do not suppress any errors that occurred
            return False

        def __getattr__(self, attr):
            if attr in ('execute', 'sendline', 'send', 'expect'):
                return getattr(self.conn, attr)

            raise AttributeError('%s object has no attribute %s'
                                 % (self.__class__.__name__, attr))
