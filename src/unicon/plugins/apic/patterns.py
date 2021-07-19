__author__ = "dwapstra"

from unicon.plugins.generic.patterns import GenericPatterns


class ApicPatterns(GenericPatterns):
    def __init__(self):
        super().__init__()
        self.enable_prompt = r'^(.*?)(%N)#'
        self.config_prompt = r'^(.*?)(%N)\(config.*\)#'
        self.shell_prompt = r'^(.*?)(\[[-\.\w]+@(%N)\s+.*?\]#)\s*(\x1b\S+)?$'


class ApicSetupPatterns(object):
    def __init__(self):
        super().__init__()
        self.fabric_name = r'^(.*?)Enter the fabric name'
        self.fabric_id = r'^(.*?)Enter the fabric ID'
        self.number_of_controllers = r'^(.*?)Enter the number of active controllers in the fabric'
        self.pod_id = r'^(.*?)Enter the POD ID'
        self.standby_controller = r'^(.*?)Is this a standby controller'
        self.controller_id = r'^(.*?)Enter the controller ID'
        self.controller_name = r'^(.*?)Enter the controller name'
        self.tep_pool = r'^(.*?)Enter address pool for TEP addresses'
        self.infra_vlan_id = r'^(.*?)Enter the VLAN ID for infra network'
        self.mc_adress_pool = r'^(.*?)Enter address pool for BD multicast addresses'
        self.enable_ipv6_oob = r'^(.*?)Enable IPv6 for Out of Band Mgmt Interface'
        self.ipv4_address = r'^(.*?)Enter the IPv4 address \['
        self.ipv4_gateway = r'^(.*?)Enter the IPv4 address of the default gateway'
        self.speed_duplex = r'^(.*?)Enter the interface speed/duplex mode'
        self.strongpw = r'^(.*?)Enable strong passwords\?'
        self.admin_pw = r'^(.*?)(Enter|Reenter) the password for admin:'
        self.edit_config = r'^(.*?)Would you like to edit the configuration\?'
