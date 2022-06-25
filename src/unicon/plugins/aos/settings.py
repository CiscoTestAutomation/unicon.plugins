'''
Author: Alex Pfeil
Contact: www.linkedin.com/in/alex-p-352040a0
Contents largely inspired by sample Unicon repo and Knox Hutchinson:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.plugins.generic import GenericSettings


class aosSettings(GenericSettings):

    def __init__(self):
        # inherit any parent settings
        super().__init__()
        self.CONNECTION_TIMEOUT = 5
        self.ESCAPE_CHAR_CALLBACK_PRE_SENDLINE_PAUSE_SEC = 3
        self.HA_INIT_EXEC_COMMANDS = []
        self.HA_INIT_CONFIG_COMMANDS = []
        self.CONSOLE_TIMEOUT = 60
        self.ATTACH_CONSOLE_DISABLE_SLEEP = 100

        # Default error pattern
        self.ERROR_PATTERN=[]
        self.CONFIGURE_ERROR_PATTERN = [
            r'.*error: +problem +checking +file:.*',
            r'.*error: +configuration +check-out +failed.*',
            r'.*Users +currently +editing +the +configuration:.*',
            r'.*error: +commit +failed:.*',
        ]

        # Maximum number of retries for password handler
        self.PASSWORD_ATTEMPTS = 3

        # User defined login and password prompt pattern.
        #self.LOGIN_PROMPT = r'^.*Login.*:'
        #self.PASSWORD_PROMPT = r'^(.*?)\w+.*[Pp]assword:'
        #self.PROXY = r'.*rhome.*\$$'

        # Ignore log messages before executing command
        self.IGNORE_CHATTY_TERM_OUTPUT = False

        # When connecting to a device via telnet, how long (in seconds)
        # to pause before checking the spawn buffer
        self.ESCAPE_CHAR_CHATTY_TERM_WAIT_RETRIES = 100
        # number of cycles to wait for if the terminal is still chatty
        self.ESCAPE_CHAR_CHATTY_TERM_WAIT = 100

        # prompt wait retries
        # (wait time: 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75 == total wait: 7.0s)
        self.ESCAPE_CHAR_PROMPT_WAIT_RETRIES = 10
        # prompt wait delay
        self.ESCAPE_CHAR_PROMPT_WAIT = 100
        
        # pattern to replace '---(more)---' or '---(more #%)---'   
        self.MORE_REPLACE_PATTERN = r'---\(more.*\)---'