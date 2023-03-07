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
from unicon.plugins.generic.service_implementation import (Execute as GenericExecute,
                                                           Configure as GenericConfigure)


logger = logging.getLogger(__name__)

class Execute(GenericExecute):
    '''
    Demonstrating how to augment an existing service by updating its call
    service method

    '''
    def call_service(self, *args, **kwargs):
        # call parent
        super().call_service(*args, **kwargs)

