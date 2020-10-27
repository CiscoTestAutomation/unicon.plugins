"""
Module:
    unicon.plugins.junos

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    This subpackage implements services specific to Junos

"""

from unicon.bases.routers.services import BaseService
from unicon.plugins.generic.service_implementation import BashService, \
                                                          Send, Sendline, \
                                                          Expect, Execute, \
                                                          Configure ,\
                                                          Enable, Disable, \
                                                          LogUser
from unicon.eal.dialogs import Dialog


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
            sm.go_to('shell', self.conn.spawn)

            return self

class Configure(Configure):
    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'config'
        self.end_state = 'enable'
        self.service_name = 'config'

    def call_service(self, command=[], reply=Dialog([]),
                      timeout=None, *args, **kwargs):
        self.commit_cmd = ('commit synchronize')
        super().call_service(command,
                             reply=reply,
                             timeout=timeout, *args, **kwargs)