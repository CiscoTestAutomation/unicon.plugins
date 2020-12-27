"""
Module:
    unicon.plugins.ironware.patterns

Author:
    James Di Trapani <james@ditrapani.com.au> - https://github.com/jamesditrapani

Description:
    This subpackage defines services specific to the Ironware OS
"""

from unicon.bases.routers.services import BaseService
from unicon.plugins.generic import ServiceList
from unicon.plugins.generic.service_implementation import Execute as GenericExec

class Execute(GenericExec):
    """
        Overwrite execute to be IronWare specific if need be
    """

    def call_service(self, *args, **kwargs):
        # call parent
        super().call_service(*args, **kwargs)

class IronWareServiceList(ServiceList):
    """
        Define IronWare specific services.
    """

    def __init__(self):
        # use the parent servies
        super().__init__()

        # overwrite and add our own
        self.execute = Execute