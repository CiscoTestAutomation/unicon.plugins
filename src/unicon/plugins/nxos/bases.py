"""
    Module:
        unicon.plugins.nxos.bases

    Authors:
        pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

    Description:
        This module provides all the base classes required for implementing
        platform which are based on NXOS.
"""
from unicon.bases.routers.connection import BaseSingleRpConnection, \
    BaseDualRpConnection


class BaseNxosSingleRpConnection(BaseSingleRpConnection):
    os='nxos'
    series = None
    chassis_type = 'single_rp'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # in case device is on a vdc, this should be updated.
        self.current_vdc = None


class BaseNxosDualRpConnection(BaseDualRpConnection):
    os='nxos'
    series = None
    chassis_type = 'dual_rp'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # in case device is on a vdc, this should be updated.
        self.current_vdc = None