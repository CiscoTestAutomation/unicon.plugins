__author__ = "Syed Raza <syedraza@cisco.com>"


from unicon.plugins.generic.patterns import GenericPatterns

# This module contains all the patterns required in the IOSXR implementation.

class IOSXRPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.enable_prompt = r'^(.*?)RP/\w+(/\S+)?/\S+\d+:(%N|ios|xr)\s?#\s?$'

        # [xr-vm_node0_RP1_CPU0:~]$
        # [xr-vm_node0_RSP1_CPU0:~]$
        # [node0_RP1_CPU0:~]$
        # #  << this is a prompt, not a comment
        self.run_prompt = r'^(.*?)(?:\[(xr-vm_)?node\d_(?:RS?P[01]|[\d+])_CPU\d:(.*?)\]\s?\$\s?|[\r\n]+\s?#\s?)$'

        # don't use hostname match in config prompt - hostname may be truncated
        # see CSCve48115 and CSCve51502
        self.config_prompt = r'^(.*?)RP/\S+\(config.*\)\s?#\s?$'
        self.exclusive_prompt = r'^(.*?)RP/\S+\(config.*\)#\s?$'
        self.telnet_prompt = r'^.*Escape character is.*'
        self.username_prompt = r'^.*([Uu]sername|[Ll]ogin):\s*$'
        self.password_prompt = r'^.*[Pp]assword:\s?$'
        self.secret_password_prompt = r'^.*Enter secret(\sagain)?:\s?$'
        self.commit_changes_prompt = r'Uncommitted changes found, commit them.*$'
        self.logout_prompt = r'^.*Press RETURN to get started\..*'
        self.commit_replace_prompt = r'Do you wish to proceed?.*$'
        self.admin_prompt = r'^(.*?)(?:sysadmin-vm:0_(.*)\s?#\s?$|RP/\S+\(admin\)\s?#\s?)$'
        self.admin_conf_prompt = r'^(.*?)(?:sysadmin-vm:0_(.*)\(config.*\)\s?#\s?|RP/\S+\(admin-config(\S+)?\)\s?#\s?)$'
        self.admin_run_prompt = r'^(.*?)(?:\[sysadmin-vm:0_.*:([\s\S]+)?\]\s?\$\s?|[\r\n]+\s?#\s?)$'
        self.unreachable_prompt = r'apples are green but oranges are red'
        self.configuration_failed_message = r'^.*Please issue \'show configuration failed \[inheritance\].*[\r\n]*'
        self.standby_prompt = r'^.*This \(D\)RP Node is not ready or active for login \/configuration.*'
        self.rp_extract_status = r'^\d+\s+(\w+)\s+\-?\d+.*$'
        self.confirm_y_prompt = r"\[confirm( with only 'y' or 'n')?\]\s*\[y/n\].*$"
        self.reload_module_prompt = r"^(.*)?Reload hardware module ? \[no,yes\].*$"
