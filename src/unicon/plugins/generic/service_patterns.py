"""
Module:
    unicon.plugins.generic.service_patterns

Authors:
    pyATS TEAM (pyats-support@cisco.com, pyats-support-ext@cisco.com)

Description:
    Module for defining all the Patterns required for the
    generic service implementation
"""
from unicon.patterns import UniconCorePatterns

class ReloadPatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        self.savenv = r"^.*System config(uration)? has been modified\.\s*Save\?.*$"
        self.confirm_reset = r'^.*Are you sure you want to reset the system\s*\(y\/n\)\?'
        self.confirm_config = r'^(.*)Uncommitted changes found.*?'
        self.autoinstall_dialog = r'^(.*)Would you like to terminate autoinstall\?\s*\[yes\]:\s*$'
        self.module_reload = r'^.*Do you want to reload the internal AP\s?\?\s((\[yes/no\]\??)|(\[y/n\]\??)):?\s?$'
        self.save_module_cfg = r'^.*Do you want to save the configuration of the AP\s?\?\s*((\[yes/no\]\??)|(\[y/n\]\??)):?\s?$'
        self.reboot_confirm = r'^(.*)This command will reboot the system.\s*\(y\/n\)\?\s*\[n\]\s?$'
        self.secure_passwd_std = r'^.*Do you want to enforce secure password standard(\?)?\s*\(yes\/no\)(\s*\[[yn]\])?\:\s*'
        self.admin_password = r'^.*(Enter|Confirm) the password for .*admin'
        self.auto_provision = r'Abort( Power On)? Auto Provisioning .*:'
        self.reload_confirm_ios = r'^.*Proceed( with reload)?\?\s*\[confirm\]'
        self.reload_confirm = r'^.*Reload node\s*\?\s*\[no,yes\]\s?$'
        self.reload_confirm_nxos = r'^(.*)This command will reboot the system.\s*\(y\/n\)\?\s*\[n\]\s?$'
        self.connection_closed = r'^(.*?)Connection.*? closed'
        self.press_return = r'Press RETURN to get started.*'


# Traceroute patterns
class TraceroutePatterns(object):
    def __init__(self):
        self.protocol = r'^.*Protocol \[.+\]\s?:\s?$'
        self.unknown_protocol = r'^.*Unknown protocol - .*help'
        self.target = r'^.*Target IP address:\s?$'
        self.ingress = r'^.*Ingress traceroute \[.+\]\s?:\s?$'
        self.source_address_interface = r'^.*Source address( or interface)?:\s?$'
        self.dscp = r'^.*DSCP .*\[.+\]\s?:\s?$'
        self.numeric_display = r'^.*Numeric display(\?)? \[.+\]\s?:\s?$'
        self.timeout_seconds = r'^.*Timeout in seconds \[.+\]\s?:\s?$'
        self.probe_count = r'^.*Probe count \[.+\]\s?:\s?$'
        self.minimum_ttl = r'^.*Minimum Time to Live \[.+\]\s?:\s?$'
        self.maximum_ttl = r'^.*Maximum Time to Live \[.+\]\s?:\s?$'
        self.port_number = r'^.*Port Number \[.+\]\s?:\s?$'
        self.style = r'^.*Loose, Strict, Record, Timestamp, Verbose\[.+\]\s?:\s?$'
        self.resolve_as_number = r'Resolve +AS +number +in.*'

# Ping patterns
class PingPatterns():
    def __init__(self):
        self.ping_loop_message = r' ^.*(% )?(Invalid source|A decimal number between|Invalid pattern|Invalid interface|No such option|Please answer).*$'
        self.unkonwn_protocol = r'^.*Unknown protocol - .*help'
        self.protocol = r'^.*Protocol \[.+\]\s?: $'
        self.transport = r'^.*traffic-eng \[.+\]\s?: $'
        self.mask = r'^.*mask: $'
        self.address = r'^.*address(( of peer)|( or Hostname))?\s?: $'
        self.vcid = r'^.*(VC|PW) ID \[.+\]\s?: $'
        self.tunnel = r'^.*Tunnel interface number \[.+\]\s?: $'
        self.repeat = r'^.*Repeat count \[.+\]\s?: $'
        self.size = r'^.*Datagram size \[.+\]\s?: $'
        self.verbose = r'^.*Verbose \[.+\]\s?: $'
        self.interval = r'^.*Interval in milliseconds \[.+\]: $'
        self.packet_timeout = r'^.*Timeout in seconds \[.+\]\s?: $'
        self.sending_interval = r'^.*Sending interval in seconds \[.+\]\s?: $'
        self.novell_echo_type = r'^.*Novell Standard Echo \[.+\]\s?: $'
        self.output_interface = r'^.*Output Interface(\[.+\])?\s?: $'
        self.vrf = r'^.*Vrf context to use \[default\] :\s?$'
        # Extended internal dialogs
        self.ext_cmds = r'^.*Extended commands.+\[.+\]\s?: $'
        self.ext_cmds_loop = r'ADD PING LOOP PATTERNS'
        self.ipv6_source = r'^.*Source address or interface\s?: $'
        self.ipv6_udp = r'^.*UDP protocol\? \[.+\]\s?: $'
        self.ipv6_priority = r'^.*Priority \[.+\]\s?: $'
        self.ipv6_verbose = r'^.*Verbose\? \[.+\]\s?: $ '
        self.ipv6_precedence = r'^.*Precedence \[.+\]\s?: $'
        self.ipv6_dscp = r'^.*DSCP \[.+\]\s?: $'
        self.ipv6_hop = r'^.*Include hop by hop option\? \[.+\]\s?: $'
        self.ipv6_dest = r'^.*Include destination option\? \[.+\]\s?: $'
        self.ipv6_extn_header = r'^.*Include extension headers\? \[.+\]\s?: $'
        self.ext_cmds_timeout = r'ADD TIMEOUT PATTERNS'
        # For IPV4
        self.dest_start = r'^.*destination start address\s?: $'
        self.interface = r'^.*Interface (\[.+\]\s?)?: $'
        self.dest_end = r'^.*Destination end address\s?: $'
        self.increment = r'^.*increment\s?: $'
        self.mpls_header = r'^.*EXP bits in mpls header \[.+\]\s?: $'
        self.tlv_pattern = r'^.*Pad TLV pattern \[.+\]\s?: $'
        self.ttl = r'^.*Time (t|T)o (L|l)ive \[.+\]\s?: $'
        self.reply_mode = r'^.*Reply mode \(.+\) \[.+\]\s?: $'
        self.revision = r'^.*LSP ping/trace revision \(.+\) \[.+\]\s?: $'
        self.null_label = r'^.*Force explicit null label.+\[.+\]\s?: $'
        self.dscp_header = r'^.*Reply (ip|IP) header DSCP bits \[.+\]\s?: $'
        self.verbomode = r'^.*Verbose mode\? \[.+\]\s?: $'
        self.ext_cmds_source = r'^.*Source .*address( or interface)?\s?: $'
        self.tos = r'^.*Type of service \[.+\]\s?: $'
        self.validate = r'^.*Validate reply data\? \[.+\]\s?: $'
        self.data_pattern = r'^.*Data pattern \[.+\]\s?: $'
        self.dfbit_header = r'^.*Set DF bit in IP header(\?)? \[.+\]\s?: $'
        self.dscp = r'^.*DSCP .*\[.+\]\s?: $'
        self.lsrtv = r'^.*Loose, Strict, Record, Timestamp, Verbose\s?\[.+\]\s?: $'
        self.qos = r'^.*Include global QOS option\? \[.+\]\s?: $'
        self.packet = r'^.*Pad packet\? \[.+\]\s?: $'
        # Range internal dialogs
        self.range = r'^.*Sweep range of sizes.* \[.+\]\s?: $'
        self.range_loop = r'ADD PING LOOP PATTERNS'
        self.range_min = r'^.*Sweep min size \[.+\]\s?: $'
        self.range_max = r'^.*Sweep max size \[.+\]\s?: $'
        self.range_interval = r'^.*Sweep interval \[.+\]\s?: $'
        self.range_timeout = r'ADD TIMEOUT PATTERNS'
        self.others = r'^.*\[.+\]\s?: $'
        #  extd_LSRTV patterns
        self.lsrtv_source = r'^.*Source route: $'
        self.lsrtv_hot_count = r'^.*Number of hops \[.*\]: $'
        self.lsrtv_timestamp_count = r'^.*Number of timestamps \[.*\]: $}'
        self.lsrtv_noroom = r'^.*No room for that option$'
        self.lsrtv_invalid_hop = r'^.*Invalid number of hops$'
        # Invalid commands
        self.invalid_command = r'^.*% *Invalid.*'


class CopyPatterns():
    def __init__(self):
        self.source_filename = r'^.*(Enter source file\s?name:.*)$'
        self.copy_file = r'^.*(file to copy|Source file name|Source filename) *\[*.*\]*\?.*$'
        self.file_to_write = r'^file to write.*\[*.*\]*.*$'
        self.hostname = r'^.*((h|H)ost|(h|H)ostname)(.*?)\[.*\]\?( *)?$'
        self.host = r'Address or name of remote host.*\?'
        self.src_file = r'Name of file to copy\?'
        self.dest_file = r'Destination filename.*$'
        self.dest_directory = r'Destination directory.*$'
        #Move this to NXOS group
        self.nx_hostname = r'^.*Enter hostname for the (tftp|ftp|scp) server:\s*$'
        self.partition = r'^.*Which partition\?.*$'
        self.config = r'^.*Name of configuration file.*\[*.*\]*.*\?'
        self.writeto = r'^.*(name to write to|[Dd]estination file ?name).*\[.*\].*$'
        self.username = r'^.*username.*(\[.*\])?.*$'
        self.password = r'^.*[Pp]assword.*(\[.*\])?.*$'
        self.erase_before_copy = r'^.*Erase .*before (writing|copying)\?\s*\[confirm\]\s*$'
        self.net_type = r'^.*Copy.*from.*\?.*\[confirm\].*$'
        self.copy_confirm = r'^.*Copy.*(from|to).*\[confirm\].*$'
        self.memory = r'^.* memory\?\s*\[confirm\]\s*$'
        self.copy_confirm_1 = r'^.*Are you sure\?.*\[confirm\]\s*$'
        self.copy_confirm_yesno = r'^.*Are you sure\?.*$'
        self.copy_reconfirm = r'^.*into Flash WITH.* erase *\?.*$'
        self.copy_progress  = r'^.*(!!!!|####|CCCC|cccc)'
        self.rcp_confirm = r'^.*(Write file|Configure using).*\?.*$'
        self.copy_overwrite = r'^.*Do you want to over\s?write\?? (\(y\/n\)\?)?\[.*\].*$'
        self.copy_nx_vrf = r'^.*Enter vrf \(If no input,.*default.*\):\s*$'
        self.copy_proceed = r'^.*bytes.*proceed\?.*$'
        self.tftp_addr =r'^.*Address.*$'
        self.copy_complete = r'^.*bank [0-9]+'
        self.copy_error_message = r'fail|timed out|Timed out|Error|Login incorrect|denied|Problem' \
                                  r'|NOT|Invalid|No memory|Failed|mismatch|Bad|bogus|lose|abort' \
                                  r'|Not |too big|exceeds|detected|[Nn]o route to host' \
                                  r'|image is not allowed|Could not resolve|No such'
        self.copy_retry_message = r'fail|[Tt]imed out|Error|Problem|NOT|Failed|Bad|bogus|lose|abort|Not |too big|exceeds|detected'
        self.copy_continue = r'Are you sure you want to continue connecting ((yes/no)|\((yes/no(/\[fingerprint\])?)?\))?'
        self.copy_other = r'^.*\[yes\/no\]\s*\?*\s*$'
        self.remote_param ='ftp:|tftp:|http:|rcp:|scp:'
        self.remote_in_dest = r'(ftp:|sftp:|tftp:|http:|rcp:|scp:)/*$'
        self.addr_in_remote = r'(ftp:|tftp:|http:|rcp:|scp:)\/*([\w\.\:]+)'

class HaReloadPatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        self.savenv = r'^.*System configuration has been modified\. Save.*$'
        self.reload_proceed = r'^(.*)Proceed with reload\?\s*\[confirm\]$|^.*Escape character is.*\n'
        self.reload_entire_shelf = r'Reload the entire shelf\s*\[confirm\]'
        self.reload_this_shelf = r'Reload this shelf\s*\[confirm\]'
        self.default_prompts = r'(Router|Switch|ios|Switch-standby)(\\(boot\\))?(>|#)'
        self.redundant = r'^.*REDUNDANCY mode is (RPR|SSO).*'
        self.config_byte = r'Uncompressed configuration from [0-9]+ bytes to [0-9]+ bytes'
        self.restriction_prompt = r'Restricted Rights Legend'
        self.login_notready = r'^.*is not ready or active for login.*'
        self.setup_dialog = r'^.*initial configuration dialog.*'
        self.autoinstall_dialog = r'^(.*)Would you like to terminate autoinstall\?\s?\[yes\]:\s*$'
        self.auto_provision = r'Abort( Power On)? Auto Provisioning.*:'
        self.sso_ready = r'Terminal state reached for (SSO)'


class SwitchoverPatterns:
    def __init__(self):
        self.save_config = r'^.*System configuration has been modified\.\s*Save\s?\?.*$'
        self.build_config= r'Building configuration'
        self.prompt_switchover = r'This will reload the active unit and force switchover to standby\[confirm\]'
        self.switchover_init = r'Preparing for switchover|LOGGER_FLUSHING|RELOAD|Reload'
        self.switchover_reason = r'^(.*)Reset Reason'
        self.switchover_fail1 = r'^(.*)Standby RP is not in RF_STANDBY_HOT state(.*)'
        self.switchover_fail2 = r'% Standby not ready for switchover\.?'
        self.switchover_fail3 = r'% There is no STANDBY present\.?'
        self.switchover_fail4 = r'Failed to switchover'
        self.switchover_cmd_issued = r'Resetting ...(.*)'

class ResetStandbyPatterns:
    def __init__(self):
        self.reload_confirm = r'Reload peer\s*\[confirm\]'
        self.reload_proceed = r'Preparing to reload peer'
        self.reset_abort = r'Peer reload not performed'
        self.reload_proceed1 = r'System is running in SIMPLEX mode, reload anyway\?\s*\[confirm\]'


reload_patterns = ReloadPatterns()
