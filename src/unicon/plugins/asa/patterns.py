from unicon.patterns import UniconCorePatterns

class ASAPatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        self.disable_prompt = r'^(.*?)(%N)(/\S+)*>\s*$'
        self.enable_prompt = r'^(.*?)(%N)(/\S+)*#\s*$'
        self.config_prompt = r'^(.*?)\(\S*(con|cfg|ipsec-profile).*\)#\s?$'
        self.line_password = r"^.+?@.+?'s +password: *$"
        self.enable_password = r'^.*Password:\s?$'
        self.bad_passwords = r'^Permission denied, please try again.$'
        self.disconnect_message = r'^Connection to .+? closed by remote host$'
        self.reload_confirm = r'^(.*?)Proceed with reload\? \[confirm\]'
        self.error_reporting = r'^(.*?)Would you like to enable anonymous error reporting to help improve the product\? \[Y\]es, \[N\]o, \[A\]sk later\s*$'
        self.save_changes = r'^(.*?)config has been modified. Save\? \[Y]es\/\[N]o\/\[S]ave all/\[C]ancel:\s*?'
        self.begin_config_replication = r'Beginning [Cc]onfiguration [Rr]eplication:? (from mate|Sending to mate)'
        self.end_config_replication = r'End [Cc]onfiguration [Rr]eplication (to|from) mate'
