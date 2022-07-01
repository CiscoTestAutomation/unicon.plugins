'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class aosPatterns():
    def __init__(self):
        logging.debug('***aosPatterns function called(%s)***')
        super().__init__()
        self.login_prompt = r'.*ogin.*'
        self.disable_mode = r'((.|\n)*>)'
        self.config_mode = r'.*config.#)'
        self.password = r'.*ssword:$'
        self.enable_prompt = r'.*#'
        self.config_prompt = r'.*config.*#)'
        self.proxy = r'.*rhome.*)'
        self.escape_char = r"Escape character is '(~)'"
        self.press_any_key = r'.*any key to conti.*'
        self.ssh_key_check = r'.*yes/no/[fingerprint]'
        self.start = r'\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*.*\r\n$'
        self.learn_os_prompt = r'^(.*?([>\$~%]|[^#\s]#|~ #|~/|^admin:|^#)\s?(\x1b\S+)?)$|(^.*This \(D\)RP Node is not ready or active for login \/configuration.*)'
