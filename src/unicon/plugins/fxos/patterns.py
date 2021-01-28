__author__ = "dwapstra"

from unicon.plugins.generic.patterns import GenericPatterns


class FxosPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.disable_prompt = r'^(.*?)(%N)(/\S+)*>\s*$'
        self.enable_prompt = r'^(.*?)(%N)(/\S+)*#\s*$'
        self.config_prompt = r'^(.*?)\(\S*(con|cfg|ipsec-profile).*\)#\s?$'
        self.username = r'^\S+ login:\s*$'

        self.ftd_prompt = r'^(.*?)\n?>\s*$'
        self.ftd_expert_prompt = r'^(.*?)[-\.\w]+@[-\.\w]+:[~/\w]+\s?\$\s*$'
        self.ftd_expert_root_prompt = r'^(.*?)[-\.\w]+@[-\.\w]+:[~/\w]+\s?#\s*$'
        self.ftd_reboot_confirm = r"Please enter 'YES' or 'NO':\s*$"

        self.fxos_prompt = r'^(.*?)[-\.\w]+(\*\s)?#\s*$'
        self.fxos_scope_prompt = r'^(.*?)[-\.\w]+(\s+(/[-\w]+)+)\*?\s?#\s*$'
        self.fxos_local_mgmt_prompt = r'^(.*?)[-\.\w]+\(local-mgmt\)#\s*$'
        self.fxos_mgmt_reboot_confirm = r'Do you still want to reboot\? \(yes/no\):\s*$'

        self.boot_interrupt = r'Use BREAK or ESC to interrupt boot'
        self.rommon_prompt = r'^(.*?)rommon.*>\s*$'

        self.cssp_pattern = r'^.*?  +Type \? for list of commands'
        self.sudo_incorrect_password_pattern = r'^.*?sudo: \d+ incorrect password attempts'

        self.bell_pattern = r'^.*\x07$'
        self.command_not_completed = r'Syntax error: The command is not completed'

        # show version glean patterns
        self.fxos_glean_pattern = r'\s*Version: '
        self.asa_glean_pattern = r'Cisco Adaptive Security Appliance Software'

        self.you_came_from_fxos = r"You came from FXOS Service Manager. Please enter 'exit' to go back."

        self.config_call_home_prompt = r'the product\? \[Y\]es, \[N\]o, \[A\]sk later:\s*$'

        self.restarting_system = r'Restarting system'
        self.system_going_down = r'The system is going down for reboot NOW'
        self.reboot_requested = r'Reboot requested by the user'
        self.boot_wait_msg = r'^.*?port-manager: Alert: (.*?) link changed to UP'
