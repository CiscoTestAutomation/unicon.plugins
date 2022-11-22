""" IOS-XE Stack Service Patterns """
from unicon.plugins.generic.service_patterns import SwitchoverPatterns, ReloadPatterns
from unicon.plugins.iosxe.patterns import IosXEPatterns

class StackIosXESwitchoverPatterns(SwitchoverPatterns):
    def __init__(self):
        super().__init__()
        self.save_config = r'^.*System configuration has been modified. Save\? \[yes\/no\]'
        self.proceed_switchover = r'^.*Proceed with switchover to standby RP\? \[confirm\]'
        self.useracess   = r'^.*User Access Verification'
        self.cisco_commit_changes_prompt = r'^(.*)Uncommitted changes found.*'
        self.terminal_state = r'.* Terminal state reached for \(SSO\).*'
        self.gen_rsh_key = r'.* Generating 1024 bit RSA keys .*'
        self.auto_provision = r'^.*Abort( Power On)? Auto Provisioning .*:'
        self.secure_passwd_std = r'^.*Do you want to enforce secure password standard(\?)? \(yes\/no\)( \[[yn]\])?\: ?'
        self.switchover_fail5 = r'Failed to switchover|Switchover aborted'
        self.press_return = r'Press RETURN to get started.*'
        self.enable_prompt = IosXEPatterns().enable_prompt
        self.disable_prompt = IosXEPatterns().disable_prompt
        self.rommon_prompt = r'(.*)switch:\s?$'
        

class StackIosXEReloadPatterns(ReloadPatterns):
    def __init__(self):
        super().__init__()
        self.reload_entire_shelf = r'^.*?Reload the entire shelf \[confirm\]'