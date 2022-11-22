__author__ = "dwapstra"

from unicon.plugins.generic.patterns import GenericPatterns


class FxosPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.disable_prompt = r'^(.*?)([-\.\w]+)(/\S+)*>\s*$'
        self.enable_prompt = r'^(.*?)([-\.\w]+)(/\S+)*#\s*$'
        self.config_prompt = r'^(.*?)\(\S*(con|cfg|ipsec-profile).*\)#\s?$'
        self.username = r'^(\S+ login:|Username:)\s*$'

        self.ftd_prompt = r'^(.*?)\n>\s*$'
        self.ftd_expert_prompt = r'^(.*?)[-\.\w]+@[-\.\w]+:[~/\w]+\s?\$\s*$'
        self.ftd_expert_root_prompt = r'^(.*?)[-\.\w]+@[-\.\w]+:[~/\w]+\s?#\s*$'
        self.ftd_reboot_confirm = r"Please enter 'YES' or 'NO':\s*$"

        self.fxos_prompt = r'^(.*?)[-\.\w]+(\*\s)?#\s*$'
        self.fxos_scope_prompt = r'^(.*?)[-\.\w]+(\s+(/[-\w]+)+)\*?\s?#\s*$'
        self.fxos_local_mgmt_prompt = r'^(.*?)[-\.\w]+\(local-mgmt\)#\s*$'
        self.fxos_mgmt_reboot_confirm = r'Do you still want to reboot\? \(yes/no\):\s*$'
        self.fxos_switch_prompt = r'^(.*?)[-\.\w]+\s?\(fxos\)#\s*$'

        self.boot_interrupt = r'(Use BREAK or ESC to interrupt boot|Use BREAK, ESC or CTRL\+L to interrupt boot)'
        self.rommon_prompt = r'^(.*?)rommon.*>\s*$'

        self.adapter_prompt = r'^(.*?)adapter \S+ #\s*$'
        self.adapter_shell_prompt = r'^(.*?)adapter \S+ \(top\):\d+#\s*$'
        self.adapter_shell_fls = r'^(.*?)adapter \S+ \(fls\):\d+#\s*$'
        self.adapter_shell_mcp = r'^(.*?)adapter \S+ \(mcp\):\d+#\s*$'

        self.cimc_prompt = r'^(.*?)\[\s+[-\w]+\s+\]#\s*$'
        self.module_prompt = r'^(.*?)Firepower-module\d+>\s*$'

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

        self.type_exit = r"Type (exit) or Ctrl-] followed by . to quit."
        self.escape_character = r"Escape character is '(~)'"

        self.ftd_console_exit = r'Connecting to ftd\(ftd\) console... enter exit to return to bootCLI'

        self.asa_is_not_running = r'asa is not running'
        self.ftd_is_not_running = r'ftd is not running'

        self.no_such_command = r'No such command'
        self.telnet_escape_prompt = r'telnet>\s?$'
