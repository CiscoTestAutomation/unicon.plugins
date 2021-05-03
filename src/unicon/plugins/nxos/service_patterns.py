"""
Module:
    unicon.plugins.nxos.services.patterns

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    Module for defining all the Patterns required for the
    nxos related service implementation
"""

class ReloadPatterns():
    def __init__(self):
        self.reload_confirm_nxos = r'^(.*)This command will reboot the system. \(y\/n\)\?  \[n\]\s?$'
        #self.useraccess = r'^.*User Access Verification'
        #self.username = r'^.*([Uu]sername|[Ll]ogin): ?$'
        #self.password = r'^.*[Pp]assword: ?$'

class HaNxosReloadPatterns:
        # NXOS reload pattern
    def __init__(self):
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
        self.skip_poap = r'^.*System is not fully online. Skip POAP\? \(yes\/no\)\[n\]:\s*$'
