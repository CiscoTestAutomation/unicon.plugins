from unicon.patterns import UniconCorePatterns
from unicon.plugins.generic.patterns import GenericPatterns


class AireosPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.base_prompt = r'^(.*?)\((%N|Cisco Capwap Simulator)\)\s*'
        self.enable_prompt = self.base_prompt + r'>\s*$'
        self.show_prompt = self.base_prompt + r'show>\s*$'
        self.config_prompt = self.base_prompt + r'config>\s*$'
        self.debug_prompt = self.base_prompt + r'debug>\s*$'
        self.test_prompt = self.base_prompt + r'test>\s*$'
        self.transfer_prompt = self.base_prompt + r'transfer>\s*$'
        self.license_prompt = self.base_prompt + r'license>\s*$'
        self.reset_prompt = self.base_prompt + r'reset>\s*$'
        self.save_prompt = self.base_prompt + r'save>\s*$'
        self.shell_prompt = r'bash.*#\s*$'
        self.standby_exec = r'^(.*?)\((%N|Cisco Capwap Simulator)-Standby\)\s*>\s*?'


class AireosReloadPatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        self.force_reboot = r'^(.*?)Do you still want to force a reboot \(y/N\)'
        self.are_you_sure = r'^(.*?)Are you sure you (would like to reset the system|want to start)\?\s*\(y/N\)'
        self.enter_user_name = r'^(.*?)Enter User Name \(.*\)'
        self.are_you_sure = r'(.*?)Are you sure.*\([yY]/[nN]\)\s*$'

class AireosPingPatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        self.bad_ping = r'Receive count=0'
        self.incorrect_ping = r'Incorrect'


class AireosCopyPatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        self.tftp_starting = r'TFTP[^\n\r]+transfer starting'
        self.tftp_complete = r'TFTP receive complete'
        self.restart_system = r'Restarting system'
        self.reboot_to_complete = r'Reboot the controller for update to complete..*to reduce network downtime'
        self.are_you_sure_save = r'Are you sure you want to save\? \(y/n\)'


class AireosExecutePatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        self.press_any_key = r'(.*?)Press any key to continue'
        self.are_you_sure = r'(.*?)Are you sure.*\([yY]/[nN]\)\s*$'
        self.press_enter_stmt = r'(.?)Press Enter to continue.*'
        self.would_you_like_to_save = r'Would you like to save them now?\? \(y/N\)'