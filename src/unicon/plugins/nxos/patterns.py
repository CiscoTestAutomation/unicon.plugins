"""
    This module contains all the patterns required in the NXOS
    implementation.
"""

from unicon.plugins.generic.patterns import GenericPatterns

class NxosPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.enable_prompt = r'^(.*?)([Rr]outer|[Ss]witch|%N)(\(standby\))?(\(maint-mode\))?#\s?$'
        self.config_prompt = r'^(?P<hostname00>.*)(\(maint-mode\))?\(.*(con|cfg|ipsec-profile)\S*\)#[\s\x07]*$'
        self.debug_prompt = r'^(.*?)Linux\(debug\)#\s*$'
        self.sqlite_prompt = r'^(.*?)sqlite>\s*$'
        self.reboot = r'This command will reboot the system. \(y\/n\)\?  \[n\]'
        self.secure_password = r'^.*Do you want to enforce secure password standard \(yes\/no\) \[y\]\:'
        self.auto_provision = r'Abort( Power On)? Auto Provisioning and continue with normal setup \?\(yes\/no\)\[n\]\:'
        self.enable_vdc = r'Do you want to enable admin vdc\s?\(yes\/no\)\s?\[n\]\:'
        self.admin_password = r'^.*(Enter|Confirm) the password for .*admin'
        self.snmp_port = r'^.*Enable the SNMP port\? \(yes\/no\) \[y\]:'
        self.boot_vdc = r'^.*Boot up system with default vdc \(yes\/no\) \[y\]\:'
        self.reload_proceed = r'^(.*)Proceed with reload\? \[confirm\]$'
        self.loader_prompt = r'^(.*)loader\s*>'
        self.redundant = r'^.*REDUNDANCY mode is (RPR|SSO).*'
        self.config_byte = r'Uncompressed configuration from [0-9]+ bytes to [0-9]+ bytes'
        self.login_notready = r'^.*is not ready or active for login.*'
        self.setup_dialog = r'^.*(initial|basic) configuration dialog.*\s?'
        self.autoinstall_dialog = r'^(.*)Would you like to terminate autoinstall\? ?\[yes\]: $'
        self.useracess = r'^.*User Access Verification'
        self.username = r'^.*([Uu]sername|[Ll]ogin): ?$'
        self.password = r'^.*[Pp]assword: ?$'
        self.run_init = r' Entering runlevel'
        self.system_up = r'System is coming up ... Please wait'
        self.delete_vdc_confirm = r'^.*Continue deleting this vdc\s?\(y\/n\)\?\s+\[no\]'
        self.shell_prompt = r'^(.*)(bash-\S+|Linux)[#\$]\s?$'
        self.commit_verification = r'^(.*)Commit +Successful.*$'
        self.module_prompt = r'^(.*?)module-\d+#\s*?$'
        self.module_elam_prompt = r'^(.*?)module-\d+(\(\w+-elam\))?#\s*?$'
        self.module_elam_insel_prompt = r'^(.*?)module-\d+(\(\w+-elam-insel\d+\))?#\s*?$'
        self.commit_changes_prompt = r'Uncommitted changes found, commit them before exiting \(yes/no/cancel\)\? \[cancel\]\s*$'
        self.nxos_module_reload = r'This command will reload module \S+ Proceed\[y\/n]\?'
        self.l2rib_dt_prompt = r'^(.*?)L2RIBCLIENT-\d+>'
