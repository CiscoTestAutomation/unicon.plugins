'''
Unicon Plugin Service
---------------------
Each method under a Unicon connection is modelled as a "service". Services must
inherit from the BaseService class, and implement call_service() method, which
acts as the entrypoint to when a service is called.
After services are defined, they should be aggregated together under a 
ServiceList class as attributes.
'''
import logging

from unicon.bases.routers.services import BaseService
from unicon.plugins.ios.iosv.service_implementation import Execute as IosvExec
from unicon.plugins.ios.iosv import IosvServiceList

logger = logging.getLogger(__name__)


class Execute(IosvExec):
    '''
    Demonstrating how to augment an existing service by updating its call
    service method
    '''

    def call_service(self, *args, **kwargs):
        # custom... code here
        logger.info('execute service called')

        # call parent
        super().call_service(*args, **kwargs)


class DellosService(BaseService):
    '''
    demonstrating the implementation of a local, new service
    '''

    def call_service(self, *args, **kwargs):
        logger.info('imaginary service called!')
        return 'Dellos' * 3


class DellosServiceList(IosvServiceList):
    '''
    class aggregating all service lists for this platform
    '''

    def __init__(self):
        # use the parent servies
        super().__init__()

        # overwrite and add our own
        self.execute = Execute
        self.dellos = DellosService
