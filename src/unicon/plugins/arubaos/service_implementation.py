'''
Author: Yannick Koehler
Contact: yannick@koehler.name
'''
import logging

from unicon.bases.routers.services import BaseService
from unicon.plugins.generic.service_implementation import Execute as GenericExecute
from unicon.plugins.generic import ServiceList

logger = logging.getLogger(__name__)


class Enable(BaseService):
    pass

class Disable(BaseService):
    pass

class Config(BaseService):
    pass

class Rommon(BaseService):
    pass 

class Shell(BaseService):
    pass

class Switchto(BaseService):
    pass
    