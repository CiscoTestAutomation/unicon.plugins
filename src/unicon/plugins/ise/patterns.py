from unicon.patterns import UniconCorePatterns


class IsePatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        self.continue_connect = r'Are you sure you want to continue connecting \(yes/no(/\[fingerprint\])?\)'
        # Prompt on ise device is <hostname>/<user-id>#.
        # If user login as root on ise device then the device
        # behaves like linux. For root login on ise use os as linux.
        # self.prompt = r'.*([^#\s]#)\s?$'
        self.prompt = r'^(.*?)%N/[A-Za-z0-9_-]+[#>]\s?$'
        self.reuse_session = r'Enter session number to resume or press <Enter> to start a new one:'
        self.config_prompt = r'^.*\(config.*\)#\s?$'
        self.more_prompt = r'^.*--More--.*'
        self.escape_char = r'Escape character is'
        self.enter_to_continue = r'Press <Enter> to continue'

