'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''
import logging

from unicon.plugins.generic.service_implementation import Execute as GenericExec
from unicon.plugins.ios.iosv import IosvServiceList

logger = logging.getLogger(__name__)


class Execute(GenericExec):
    '''
    Demonstrating how to augment an existing service by updating its call
    service method
    '''

    def call_service(self, *args, **kwargs):
        # custom... code here
        logger.info('execute service called')

        # call parent
        super().call_service(*args, **kwargs)


class aosServiceList(IosvServiceList):
    '''
    class aggregating all service lists for this platform
    '''

    def __init__(self):
        # use the parent servies
        super().__init__()

        # overwrite and add our own
        self.execute = Execute