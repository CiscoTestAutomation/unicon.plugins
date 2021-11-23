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
        self.commit_cmd = 'commit'