__author__ = "dwapstra"

from unicon.plugins.generic.patterns import GenericPatterns

class FtdPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.chassis_prompt = r'^(.*?)[-\.\w]+(\*\s)?#\s*$'
        self.chassis_scope_prompt = r'^(.*?)[-\.\w]+(\s+(/[-\w]+)+)\*?\s?#\s*$'
        self.fxos_prompt = r'^(.*?)[-\.\w]+\s?\(fxos\)#\s*$'
        self.local_mgmt_prompt = r'^(.*?)[-\.\w]+\(local-mgmt\)#\s*$'
        self.cimc_prompt = r'^(.*?)\[\s+[-\w]+\s+\]#\s*$'
        self.module_console_prompt = r'^(.*?)Firepower-module\d+>\s*$'

        # ftd console prompt overlaps with module console, pattern match includes non-digit before prompt char (>)
        self.ftd_console_prompt = r'^(.*?)([^\d]+)[\r\n]*>\s*$'
        self.ftd_expert_prompt = r'^(.*?)[-\.\w]+@Firepower-module\d+:[/\w]+\s?\$\s*$'
        self.ftd_expert_root_prompt = r'^(.*?)[-\.\w]+@Firepower-module\d+:[~/\w]+\s?#\s*$'

        self.cssp_pattern = r'^.*?  +Type \? for list of commands'
        self.sudo_incorrect_password_pattern = r'^.*?sudo: \d+ incorrect password attempts'

        self.command_not_completed = r'Syntax error: The command is not completed'

        self.are_you_sure = r'(.*?)Are you sure.*?\(yes\/no\)\s*$'