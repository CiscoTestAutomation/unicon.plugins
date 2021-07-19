__author__ = "dwapstra"

import re
from time import sleep

from unicon.core.errors import SubCommandFailure, StateMachineError
from unicon.bases.routers.services import BaseService
from unicon.eal.dialogs import Dialog, Statement

from unicon.plugins.generic.statements import GenericStatements
from unicon.plugins.generic import GenericUtils

from ..patterns import FxosPatterns
from .statements import FtdStatements

utils = GenericUtils()
ftd_statements = FtdStatements()
generic_statements = GenericStatements()


class Switchto(BaseService):
    """ Switch to a certain CLI state
    """

    def __init__(self, connection, context, **kwargs):
        # Connection object will have all the received details
        super().__init__(connection, context, **kwargs)
        self.timeout = connection.settings.EXEC_TIMEOUT
        self.context = context

    def log_service_call(self):
        pass

    def pre_service(self, target, *args, **kwargs):

        if not self.connection.connected:
            self.connection.log.warning('Device is not connected, ignoring switchto')
            return

        self.connection.log.info("+++ %s: %s +++" % (self.service_name, target))

    def call_service(self, target,
                     timeout=None,
                     *args, **kwargs):

        if not self.connection.connected:
            return

        con = self.connection
        sm = self.get_sm()

        dialog = Dialog([ftd_statements.command_not_completed_stmt])

        timeout = timeout if timeout is not None else self.timeout

        if isinstance(target, str):
            target_list = [target]
        elif isinstance(target, list):
            target_list = target
        else:
            raise Exception('Invalid switchto target type: %s' % repr(target))

        for target_state in target_list:
            m1 = re.match('module\s+(\d+)\s+console', target_state)
            m2 = re.match('cimc\s+(\S+)', target_state)
            m3 = re.match('chassis scope (.*)', target_state)
            if m1:
                mod = m1.group(1)
                self.context._module = mod
                target_state = 'module_console'
            elif m2:
                mod = m2.group(1)
                self.context._cimc_module = mod
                target_state = 'cimc'
                con.state_machine.go_to('chassis', con.spawn,
                                        context=self.context,
                                        hop_wise=True,
                                        timeout=timeout)
            elif m3:
                scope = m3.group(1)
                self.context._scope = scope
                target_state = 'chassis_scope'
                con.state_machine.go_to('chassis', con.spawn,
                                        context=self.context,
                                        hop_wise=True,
                                        timeout=timeout)
            else:
                target_state = target.replace(' ', '_')

            valid_states = [x.name for x in sm.states]
            if target_state not in valid_states:
                con.log.warning('%s is not a valid state, ignoring switchto' % target_state)
                return

            con.state_machine.go_to(target_state, con.spawn,
                                        context=self.context,
                                        hop_wise=True,
                                        timeout=timeout,
                                        dialog=dialog)

        self.end_state = sm.current_state

    def post_service(self, *args, **kwargs):
        pass

