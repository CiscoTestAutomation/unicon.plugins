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
from unicon.plugins.generic import ServiceList
from unicon.plugins.generic.service_implementation import (Execute as GenericExecute,
                                                           Configure as GenericConfigure)


logger = logging.getLogger(__name__)

class Execute(GenericExecute):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'operation'
        self.end_state = 'operation'

    '''
    Demonstrating how to augment an existing service by updating its call
    service method

    '''
    def call_service(self, *args, **kwargs):
        # custom... code here
        logger.info('execute service called')

        # call parent
        super().call_service(*args, **kwargs)

class DnosService(BaseService):
    '''
    demonstrating the implementation of a local, new service
    '''
    def call_service(self, *args,**kwargs):
        logger.info('example service called!')
        return 'example service called!'

class DnosServiceList(ServiceList):
    '''
    class aggregating all service lists for this platform
    '''

    def __init__(self):
        # use the parent services
        super().__init__()

        # overwrite and add our own
        self.execute = Execute
        self.example = DnosService
        