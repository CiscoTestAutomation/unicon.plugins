'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo, Knox Hutchinson and pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com):
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''
#This portion of the script is still a work in progress.
import io
import re
import collections
import warnings

from time import sleep
from datetime import datetime, timedelta

from unicon.core.errors import TimeoutError
from unicon.settings import Settings
from .patterns import aosPatterns
#This enables logging in the script.
import logging
#Logging disable disables logging in the script. In order to turn on logging, comment out logging disable.
logging.disable(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

patterns = aosPatterns()
settings = Settings()
    
    
def __init__(self, connection, context, **kwargs):
    logging.debug('***SP Serivce Implementation called(%s)***')
    self.start_state = 'exec'
    self.end_state = 'exec'