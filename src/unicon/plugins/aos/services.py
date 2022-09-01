'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo, Knox Hutchinson and pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com):
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''
from unicon.plugins.generic.service_implementation import Execute as GenericExec
from unicon.plugins.ios.iosv import IosvServiceList
#This enables logging in the script.
import logging
#Logging disable disables logging in the script. In order to turn on logging, comment out logging disable.
logging.disable(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')



class Execute(GenericExec):
    '''
    Demonstrating how to augment an existing service by updating its call
    service method
    '''
    logging.debug('***Services Execute Class called(%s)***')
    def call_service(self, *args, **kwargs):
        # custom... code here
        logging.debug('***Services call service function called(%s)***')

        # call parent
        super().call_service(*args, **kwargs)

class aosServiceList(IosvServiceList):
    '''
    class aggregating all service lists for this platform
    '''
    logging.debug('***Services aosServiceList called(%s)***')
    def __init__(self):
        # use the parent servies
        super().__init__()
        logging.debug('***Services aosServiceList function called(%s)***')
        # overwrite and add our own
        self.execute = Execute
        
