"""
Module:
    unicon.plugins.hvrp
Authors:
    Miguel Botia (mibotiaf@cisco.com), Leonardo Anez (leoanez@cisco.com)
Description:
    This subpackage implements services specific to HVRP.
"""

from unicon.plugins.generic.service_implementation import BashService, \
                                                          Send, Sendline, \
                                                          Expect, Execute, \
                                                          Configure ,\
                                                          Enable, Disable, \
                                                          LogUser


class Configure(Configure):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'config'
        self.end_state = 'enable'
        self.service_name = 'config'

    def pre_service(self, *args, **kwargs):
        super().pre_service(*args, **kwargs)

        # Check if device is operating in two-stage configuration mode.
        # =============================================================
        spawn = self.get_spawn()
        two_stage = spawn.match.last_match.groupdict().get('two_stage')

        # In the two-stage mode, if the user has modified configurations but has
        # not submit the modification, the system prompt ~ is changed to *,
        # prompting the user that the configurations are not submitted. After
        # the user runs the commit command to submit the configurations, the
        # system prompt * is restored to ~.

        if two_stage:
            self.commit_cmd = 'commit'
        else:
            self.commit_cmd = ''
