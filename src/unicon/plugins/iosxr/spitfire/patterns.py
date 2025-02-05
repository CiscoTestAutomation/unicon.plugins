__author__ = "Sritej K V R <skanakad@cisco.com>"

from unicon.plugins.iosxr.patterns import IOSXRPatterns

class SpitfirePatterns(IOSXRPatterns):
    def __init__(self):
        super().__init__()
        # Always have the first match group (.*?) as this is the data
        # returned as the cli output .
        self.bmc_prompt = \
            r'^(.*?)root@spitfire-arm:.+?#\s*?$'
        self.xr_bash_prompt = \
            r'^(.*?)(?<!XR)\[(ios|%N):.+?\]\$\s*?$'
        self.xr_run_prompt = \
            r'^(.*?)\[node\d_(?:RP[01]|[\d+])_CPU\d:.+?\]\$\s*?$'
        self.bmc_login_prompt = \
            r'^(.*?)spitfire-arm login:\s*?$'
        self.xr_env_prompt = \
            r'^(.*?)XR\[(ios|%N):(?:~|.+?)\]\$\s*?$'
        self.bad_passwords = \
            r'^.*?% (Bad passwords|Access denied|Authentication failed|Login incorrect)'
        self.confirm_prompt = \
            r'^(.*?)\[confirm\]\s*\s*?$'
        self.username_prompt = \
            r'^.*([Uu]sername|[Ll]ogin):\s*?$'
        self.password_prompt = \
            r'^.*[Pp]assword:\s*?$'
        self.showtech_graceful_exit = \
            r'^(.*?)[Dd]o [Yy]ou [Ww]ish [Tt]o [Tt]erminate\?\s*\((Y|y|YES|Yes|yes)\/(N|n|NO|No|no)\)\s*:\s*?$'

        self.xr_module_prompt = r'(?m)(.*?)^#\s*$'
