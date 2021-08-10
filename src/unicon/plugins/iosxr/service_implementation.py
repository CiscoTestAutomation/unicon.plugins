__author__ = "Syed Raza <syedraza@cisco.com>"

import re
from time import sleep
from datetime import datetime, timedelta

from unicon.plugins.generic import service_implementation as svc
from unicon.bases.routers.services import BaseService
from unicon.core.errors import SubCommandFailure
from unicon.eal.dialogs import Dialog, Statement
from unicon.plugins.generic.service_implementation import BashService
from unicon.plugins.generic.service_implementation import GetRPState as GenericGetRPState

from .service_statements import (switchover_statement_list,
                                 config_commit_stmt_list,
                                 execution_statement_list)

from .utils import IosxrUtils

utils = IosxrUtils()

def get_commit_cmd(**kwargs):
    if 'force' in kwargs and kwargs['force'] is True:
        commit_cmd = 'commit force'
    elif 'replace' in kwargs and kwargs['replace'] is True:
        commit_cmd = 'commit replace'
    else:
        commit_cmd = 'commit'
    return commit_cmd


class Execute(svc.Execute):
    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.dialog += Dialog(execution_statement_list)


class Configure(svc.Configure):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'config'
        self.end_state = 'enable'

    def call_service(self, command=[], reply=Dialog([]),
                     timeout=None, *args, **kwargs):
        self.commit_cmd = get_commit_cmd(**kwargs)
        super().call_service(command,
                             reply=reply + Dialog(config_commit_stmt_list),
                             timeout=timeout, *args, **kwargs)


class ConfigureExclusive(Configure):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'exclusive'
        self.end_state = 'enable'
        self.service_name = 'exclusive'


class HaConfigureService(svc.HaConfigureService):
    def call_service(self, command=[], reply=Dialog([]), target='active',
                     timeout=None, *args, **kwargs):
        self.commit_cmd = get_commit_cmd(**kwargs)
        super().call_service(command,
                             reply=reply + Dialog(config_commit_stmt_list),
                             target=target, timeout=timeout, *args, **kwargs)


class Reload(svc.Reload):

    def call_service(self, reload_command='reload', *args, **kwargs):
        super().call_service(reload_command, *args, **kwargs)


class HaReload(svc.HAReloadService):
    def call_service(self, command=[], reload_command=[], reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        if command:
            super().call_service(command,
                                 timeout=timeout, *args, **kwargs)
        else:
            super().call_service(reload_command=reload_command or "reload",
                                 timeout=timeout, *args, **kwargs)


class AdminExecute(Execute):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'admin'
        self.end_state = 'enable'


class AdminConfigure(Configure):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'admin_conf'
        self.end_state = 'enable'


class HAExecute(svc.HaExecService):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog += Dialog(execution_statement_list)


class HaAdminExecute(AdminExecute):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'admin'
        self.end_state = 'enable'


class HaAdminConfigure(HaConfigureService):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'admin_conf'
        self.end_state = 'enable'


class Switchover(BaseService):
    """ Service to switchover the device.

    Arguments:
        command: command to do switchover. default
                 "redundancy switchover"
        dialog: Dialog which include list of Statements for
                additional dialogs prompted by switchover command,
                in-case it is not in the current list.
        timeout: Timeout value in sec, Default Value is 500 sec

    Returns:
        True on Success, raise SubCommandFailure on failure.

    Example:
        .. code-block:: python

            rtr.switchover()
            # If switchover command is other than 'redundancy switchover'
            rtr.switchover(command="command which invoke switchover",
            timeout=700)
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.timeout = connection.settings.SWITCHOVER_TIMEOUT
        self.dialog = Dialog(switchover_statement_list)

    def call_service(self, command='redundancy switchover',
                     dialog=Dialog([]),
                     timeout=None,
                     sync_standby=True,
                     error_pattern=None,
                     *args,
                     **kwargs):
        # create an alias for connection.
        con = self.connection

        if error_pattern is None:
            self.error_pattern = con.settings.ERROR_PATTERN
        else:
            self.error_pattern = error_pattern

        start_time = datetime.now()
        timeout = timeout or self.timeout

        con.log.debug("+++ Issuing switchover on  %s  with "
                      "switchover_command %s and timeout is %s +++"
                      % (con.hostname, command, timeout))

        dialog += self.dialog

        # Issue switchover command
        con.active.spawn.sendline(command)
        try:
            self.result = dialog.process(con.active.spawn,
                           timeout=self.timeout,
                           prompt_recovery=self.prompt_recovery,
                           context=con.active.context)
        except SubCommandFailure as err:
            raise SubCommandFailure("Switchover Failed %s" % str(err))

        output = ""
        if self.result:
            self.result = self.get_service_result()
            output += self.result.match_output

        con.log.info('Switchover done, switching sessions')
        con.active.spawn.sendline()
        con.standby.spawn.sendline()
        con.connection_provider.prompt_recovery = True
        con.connection_provider.connect()
        con.connection_provider.prompt_recovery = False

        if sync_standby:
            con.log.info('Waiting for standby state')

            delta_time = timedelta(seconds=timeout)
            current_time = datetime.now()
            while (current_time - start_time) < delta_time:
                show_redundancy = con.execute('show redundancy', prompt_recovery=True)
                standby_state = re.findall(con.settings.STANDBY_STATE_REGEX, show_redundancy)
                standby_state = [s.strip() for s in standby_state]
                con.log.info('Standy state: %s' % standby_state)
                if standby_state == con.settings.STANDBY_EXPECTED_STATE:
                    break
                wait_time = con.settings.STANDBY_STATE_INTERVAL
                con.log.info('Waiting %s seconds' % wait_time)
                sleep(wait_time)
                current_time = datetime.now()

            if current_time - start_time > delta_time:
                raise SubCommandFailure('Switchover timed out, standby state: %s' % standby_state)

        # TODO: return all/most console output, not only from the switchover
        # This requires work on the bases.router.connection_provider BaseDualRpConnectionProvider implementation
        self.result = output


class AttachModuleConsole(BaseService):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_state = "enable"
        self.end_state = "enable"

    def call_service(self, module_num, **kwargs):
        self.result = self.__class__.ContextMgr(connection = self.connection,
                                                module_num = module_num,
                                                **kwargs)

    class ContextMgr(object):
        def __init__(self, connection,
                           module_num,
                           login_name = 'root',
                           change_prompt = '#',
                           timeout = None):
            self.conn = connection
            self.module_num = module_num
            self.login_name = login_name
            self.change_prompt = change_prompt
            self.timeout = timeout or connection.settings.CONSOLE_TIMEOUT

        def __enter__(self):
            self.conn.log.debug('+++ attaching console +++')
            # attach to console
            self.conn.sendline('attach location %s' % self.module_num)
            try:
                match = self.conn.expect([r"export PS1=\'\#\'.*[\r\n]*\#"],
                                          timeout = self.timeout)
            except SubCommandFailure:
                pass

            return self

        def execute(self, command, timeout = None):
            # take default if not set
            timeout = timeout or self.timeout

            # send the command
            self.conn.sendline(command)

            # expect output until prompt again
            # wait for timeout provided by user
            out = self.conn.expect([r'(.+)[\r\n]*%s$' % self.change_prompt], timeout=timeout)
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
            self.conn.expect([r'.+'], timeout = self.timeout)

            # get out
            self.conn.sendline('exit')
            self.conn.expect([r'(.+)%s\#' % self.conn.hostname], timeout = self.timeout)

            # do not suppress
            return False

        def __getattr__(self, attr):
            if attr in ('sendline', 'send'):
                return getattr(self.conn, attr)

            raise AttributeError('%s object has no attribute %s'
                                 % (self.__class__.__name__, attr))


class AdminAttachModuleConsole(AttachModuleConsole):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_state = "admin"
        self.end_state = "enable"

    class ContextMgr(AttachModuleConsole.ContextMgr):

        def __init__(self, connection,
                           module_num,
                           login_name = 'root',
                           change_prompt = r'\~(.+)?\]\$',
                           timeout = None):
            self.conn = connection
            self.module_num = module_num
            self.login_name = login_name
            self.change_prompt = change_prompt
            self.timeout = timeout or connection.settings.CONSOLE_TIMEOUT

        def __enter__(self):
            self.conn.log.debug('+++ attaching console +++')

            sm = self.conn.state_machine
            sm.go_to('admin', self.conn.spawn)

            # attach to console
            self.conn.sendline('attach location %s' % self.module_num)
            try:
                match = self.conn.expect([r"%s" % self.change_prompt],
                                          timeout = self.timeout)
            except SubCommandFailure:
                pass

            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not SubCommandFailure:
                # exit from attached location
                admin = self.conn.state_machine.get_state('admin')
                self.conn.sendline('exit')
                self.conn.expect(admin.pattern, timeout = self.timeout)
            return super().__exit__(exc_type, exc_val, exc_tb)


class AdminService(BashService):

    class ContextMgr(BashService.ContextMgr):
        def __init__(self, connection,
                           enable_bash = False,
                           timeout = None):
            # overwrite the prompt
            super().__init__(connection=connection,
                             enable_bash=enable_bash,
                             timeout=timeout)

        def __enter__(self):
            self.conn.log.debug('+++ attaching admin shell +++')

            sm = self.conn.state_machine
            sm.go_to('admin', self.conn.spawn)

            return self


class BashService(BashService):

    class ContextMgr(BashService.ContextMgr):
        def __init__(self, connection,
                           enable_bash = False,
                           timeout = None):
            # overwrite the prompt
            super().__init__(connection=connection,
                             enable_bash=enable_bash,
                             timeout=timeout)

        def __enter__(self):
            self.conn.log.debug('+++ attaching bash shell +++')

            sm = self.conn.state_machine

            if hasattr(self.conn, 'platform') and \
                self.conn.platform == 'spitfire':
                # In case of spitfire plugin
                sm.go_to('xr_run', self.conn.spawn)
            else:
                sm.go_to('run', self.conn.spawn)

            return self

class AdminBashService(BashService):

    class ContextMgr(BashService.ContextMgr):
        def __init__(self, connection,
                           enable_bash = False,
                           timeout = None):
            # overwrite the prompt
            super().__init__(connection=connection,
                             enable_bash=enable_bash,
                             timeout=timeout)

        def __enter__(self):
            self.conn.log.debug('+++ attaching bash shell +++')


            sm = self.conn.state_machine
            sm.go_to('admin_run', self.conn.spawn)

            return self


class GetRPState(GenericGetRPState):
    """ Get Rp state

    Service to get the redundancy state of the device rp.
    Returns standby rp state if standby is passed as input.

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
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'any'
        self.end_state = 'any'

    def call_service(self,
                     target='active',
                     timeout=None,
                     utils=utils,
                     *args,
                     **kwargs):

        """send the command on the right rp and return the output"""
        return super().call_service(target=target, timeout=timeout, utils=utils, *args, **kwargs)
