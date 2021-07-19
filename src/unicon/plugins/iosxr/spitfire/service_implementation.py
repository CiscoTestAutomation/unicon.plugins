__copyright__ = "# Copyright (c) 2019 by cisco Systems, Inc. All rights reserved."
__author__ = "skanakad"

from unicon.bases.routers.services import BaseService
from unicon.eal.dialogs import Dialog, Statement

from .statements import SpitfireStatements

statements = SpitfireStatements()


class Switchto(BaseService):
    """ Switch to a certain CLI state
    """

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.context = context

    def log_service_call(self):
        pass

    def pre_service(self, target_state, *args, **kwargs):

        if not self.connection.is_connected:
            self.connection.log.warning('Device is not connected, ignoring switchto')
            return

        if self.get_sm().current_state == target_state:
            self.connection.log.info("Device already at the target state %s" % (target_state))
            return
        self.connection.log.info("+++ %s: %s +++" % (self.service_name, target_state))

    def call_service(self, target_state,
                     timeout=None,
                     *args, **kwargs):

        if not self.connection.is_connected:
            return

        con = self.get_handle()
        sm = self.get_sm()

        login_dialog = Dialog([
            statements.bmc_login_stmt,
            statements.password_stmt,
            statements.login_stmt
            ])
        timeout = timeout if timeout is not None else self.timeout

        valid_states = [x.name for x in sm.states]
        if target_state not in valid_states:
            con.log.warning('%s is not a valid state, ignoring switchto' % target_state)
            return

        if sm.current_state == 'xr_env':
            con.sendline('exit')
            con.state_machine.go_to(['xr_bash', 'xr_run'], con.spawn,
                                    context=self.context,
                                    hop_wise=False,
                                    timeout=timeout,
                                    dialog=login_dialog)

        con.state_machine.go_to(target_state, con.spawn,
                                context=self.context,
                                hop_wise=True,
                                timeout=timeout,
                                dialog=login_dialog)

        self.end_state = sm.current_state

    def post_service(self, *args, **kwargs):
        pass


