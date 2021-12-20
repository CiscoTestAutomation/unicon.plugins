"""
Module:
    unicon.plugins.generic

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    Module for defining all the Patterns required for the
    generic implementation
"""
from unicon.patterns import UniconCorePatterns

class GenericPatterns(UniconCorePatterns):

    """
        Class defines all the patterns required
        for generic
    """

    def __init__(self):

        """ initialises all generic patterns
        """
        super().__init__()
        # self.enable_prompt = r'.*%N#\s?$'
        self.default_hostname_pattern = r'WLC|RouterRP|Router|[Ss]witch|Controller|ios'

        self.enable_prompt = r'^(.*?)(Router|Router-stby|Router-sdby|RouterRP|RouterRP-standby|%N-standby|%N\(standby\)|%N-sdby|%N-stby|(S|s)witch|(S|s)witch\(standby\)|Controller|ios|-Slot[0-9]+|%N)(\(boot\))*#\s?$'

        # self.disable_prompt = r'.*%N>\s?$'
        self.disable_prompt = r'^(.*?)(Router|Router-stby|Router-sdby|RouterRP|RouterRP-standby|%N-standby|%N-sdby|%N-stby|(S|s)witch|s(S|s)witch\(standby\)|Controller|ios|-Slot[0-9]+|%N)(\(boot\))*>\s?$'

        # self.config_prompt = r'.*%N\(config.*\)#\s?$'
        self.config_prompt = r'^(.*)\(.*(con|cfg|ipsec-profile|ca-trustpoint|gkm-local-server)\S*\)#\s?$'
        self.rommon_prompt = r'^(.*?)(rommon[\s\d]*>|switch:)\s?$'
        # self.standby_enable_prompt = r'^(.*?)(RouterRP-standby|%N-standby|%N-sdby|%N\(standby\))#\s?$'
        # self.standby_disable_prompt = r'^(.*?)(RouterRP-standby|%N-standby|%N-sdby|%N\(standby\))>\s?$'
        self.standby_locked = r'[S|s]tandby console disabled'
        self.shell_prompt = r'^(.*)%N\(shell\)>\s?'

        self.disconnect_message = r'Received disconnect from .*:'
        self.password_ok = r'Password OK\s*$'

        self.continue_connect = r'Are you sure you want to continue connecting \(yes/no(/\[fingerprint\])?\)'

        self.cisco_commit_changes_prompt = r'Uncommitted changes found, commit them\? \[yes/no/CANCEL\]'
        self.juniper_commit_changes_prompt = r'Discard changes and continue\? \[yes,no\]'

        self.hit_enter = r'Hit Enter to proceed:'
        self.press_ctrlx = r"^(.*?)Press Ctrl\+x to Exit the session"
        self.connected = r'^(.*?)Connected.'

        self.enter_basic_mgmt_setup = r'Would you like to enter basic management setup\? \[yes/no\]:'
        self.kerberos_no_realm = r'^(.*)Kerberos:\s*No default realm defined for Kerberos!'

        self.passphrase_prompt = r'^.*Enter passphrase for key .*?:\s*?'

        self.learn_os_prompt = r'^(.*?([>\$~%]|[^#\s]#|~ #|~/|^admin:|^#)\s?(\x1b\S+)?)$|(^.*This \(D\)RP Node is not ready or active for login \/configuration.*)'

        self.sudo_password_prompt = r'^.*\[sudo\] password for .*?:\s*?'

        # *Sep 6 23:13:38.188: %PNP-6-PNP_SDWAN_STARTED: PnP SDWAN started (7) via (pnp-sdwan-abort-on-cli) by (pid=3, pname=Exec)
        # *Sep 6 23:18:11.702: %ENVIRONMENTAL-1-ALERT: Temp: Inlet 1, Location: R0, State: Warning, Reading: 45 Celsius
        # *Sep 6 17:43:41.291: %Cisco-SDWAN-RP_0-CFGMGR-4-WARN-300005: New admin password not set yet, waiting for daemons to read initial config.
        self.syslog_message_pattern = r'^.*?%\w+(-\S+)?-\d+-\w+.*$'

        self.config_locked = r'Configuration (mode )?(is )?locked|Config mode cannot be entered'

        self.config_start = r'Enter configuration commands, one per line\.\s+End with CNTL/Z\.\s*$'

        self.enable_secret = r'^.*?(Enter|Confirm) enable secret:\s*$'

        self.enter_your_selection_2 = r'^.*?Enter your selection( \[2])?:\s*$'

        self.guestshell_prompt = r'^(.*)\[\S+@guestshell\s+.*\][#\$]\s?$'

        self.press_any_key = r'^.*?Press any key to continue\.\s*$'

