"""Implementation of services related to the iosxe/c9800/ewc Unicon plugin

Copyright (c) 2019-2020 by cisco Systems, Inc.
All rights reserved.
"""

from unicon.bases.routers.services import BaseService
from unicon.eal.dialogs import Dialog
from unicon.plugins.iosxe.service_implementation import BashService as IosXEBashService
from unicon.plugins.generic.service_implementation import \
    Execute as GenericExecute
from unicon.eal.dialogs import Dialog
from unicon.plugins.iosxe.service_statements import confirm

from .patterns import IosXEEWCBashShellPatterns, IosXEEWCAPShellPatterns
from .service_statements import enter_bash_shell_statement_list
from .settings import IosXEEWCBashShellSettings, IosXEEWCAPShellSettings

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Bash Shell service implementation
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
bash_shell_settings = IosXEEWCBashShellSettings()
bash_shell_patterns = IosXEEWCBashShellPatterns()


class Execute(GenericExecute):
    def call_service(self, command=None, reply=Dialog([]), timeout=None, *args,
                     **kwargs):
        command = list() if command is None else command
        super().call_service(command,
                             reply=reply + Dialog([confirm,]),
                             timeout=timeout, *args, **kwargs)


class IosXEEWCBashService(IosXEBashService):

    def pre_service(self, *args, **kwargs):
        if kwargs.get('chassis'):
            self.context['_chassis'] = kwargs.get('chassis')

        super().pre_service(self,args,kwargs)
    class ContextMgr(IosXEBashService.ContextMgr):

        def __enter__(self):
            conn = self.conn
            conn.log.debug('+++ attaching iosxe ewc bash shell +++')

            conn.state_machine.hostname = bash_shell_patterns.coral_hostname
            bash_shell_dialog = Dialog(enter_bash_shell_statement_list)
            command = "request platform software system shell chassis {} R0".format(
                conn.context.get('_chassis', '1'))
            conn.sendline(command)
            bash_shell_dialog.process(conn.spawn, conn.context,
                                      timeout=bash_shell_settings.CONSOLE_TIMEOUT)

            for cmd in conn.settings.BASH_INIT_COMMANDS:
                conn.execute(cmd, timeout=self.timeout)
            return self

        def __exit__(self, exc_type, exc_value, exc_tb):
            conn = self.conn
            conn.log.debug('--- detaching console ---')
            conn.sendline('exit')
            return False  # do not suppress

    def post_service(self, *args, **kwargs):
        self.context.pop('_chassis', None)

        super().post_service(self,args,kwargs)


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# AP Shell service implementation
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
ap_shell_settings = IosXEEWCAPShellSettings()
ap_shell_patterns = IosXEEWCAPShellPatterns()


class EWCApShellService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_state = "enable"
        self.end_state = "enable"
        self.service_name = "ap_shell"

    def call_service(self, **kwargs):
        self.result = self.__class__.ContextMgr(connection=self.connection, **kwargs)

    class ContextMgr(object):
        def __init__(self, connection, **kwargs):
            timeout = kwargs.get('timeout')
            self.conn = connection
            self.timeout = timeout or ap_shell_settings.EWC_AP_TIMEOUT

        def __enter__(self):
            conn = self.conn
            conn.log.debug('+++ attaching ap shell +++')

            conn.state_machine.go_to(
                'ap_enable',
                spawn=conn.spawn,
                context=conn.context)

            for command in ap_shell_settings.HA_INIT_EXEC_COMMANDS:
                conn.execute(command, timeout=self.timeout)
            return self

        def __exit__(self, *args, **kwargs):
            conn = self.conn
            conn.log.debug('--- detaching console ---')
            conn.state_machine.go_to(
                'enable',
                spawn=conn.spawn,
                context=conn.context)
            return False  # do not suppress

        def __getattr__(self, attr):
            return getattr(self.conn, attr)
