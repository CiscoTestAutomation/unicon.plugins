'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

"""
Module:
    unicon.plugins.generic

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    Module for defining all the Patterns required for the
    generic implementation
"""
from unicon.patterns import UniconCorePatterns
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class aosPatterns(UniconCorePatterns):
    def __init__(self):
        logging.debug('***aosPatterns function called(%s)***')
        super().__init__()
        self.login_prompt = r'.*ogin.*'
        self.password_prompt = r'^.*[Pp]assword( for )?(\\S+)?: ?$'
        self.enable_prompt = r'.*>'
        self.config_mode = r'.*config.#'
        self.password = r'.*ssword:$'
        self.executive_prompt = r'.*#'
        self.config_prompt = r'.*config.*#'
        self.proxy = r'.*rhome.*'
        self.press_any_key = r'.*any key to conti.*'
        self.ssh_key_check = r'.*yes/no/[fingerprint]'
        self.start = r'.*These computing resources are solely owned by the Company. Unauthorized\r\naccess, use or modification is a violation of law and could result in\r\ncriminal prosecution. Users agree not to disclose any company information\r\nexcept as authorized by the Company. Your use of the Company computing\r\nresources is consent to be monitored and authorization to search your\r\ncomputer or device to assure compliance with company policies and/or the law.*'
        self.learn_os_prompt = r'^(.*?([>\$~%]|[^#\s]#|~ #|~/|^admin:|^#)\s?(\x1b\S+)?)$|(^.*This \(D\)RP Node is not ready or active for login \/configuration.*)'
