__author__ = "Sritej K V R <skanakad@cisco.com>"

from unicon.plugins.iosxr.settings import IOSXRSettings

class SpitfireSettings(IOSXRSettings):
    
    CONFIG_LOCK_TIMEOUT = 600
    def __init__(self):
        super().__init__()
        self.SPITFIRE_INIT_EXEC_COMMANDS = [
            'term length 0',
            'term width 0',
            'show version',
            'bash cat /etc/bake-info.txt',
            'bash cat /etc/build-info.txt'
        ]
        self.ERROR_PATTERN = ['Invalid input detected at \'^\' marker']
        self.SPITFIRE_INIT_CONFIG_COMMANDS = [
            'logging console disable',
            'line console',
            'exec-timeout 0 0',
            'absolute-timeout 0',
            'session-timeout 0',
            'line default',
            'exec-timeout 0 0',
            'absolute-timeout 0',
            'session-timeout 0'
        ]
        self.CONFIG_TIMEOUT = 600
        self.STANDBY_STATE_REGEX = r'Standby node .* is (.*)'
