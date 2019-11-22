__author__ = "Myles Dear <mdear@cisco.com>"

from unicon.plugins.iosxe.patterns import IosXEPatterns


class IosXECsr1000vPatterns(IosXEPatterns):
    def __init__(self):
        super().__init__()

        # Saw the following line in the CSR1000V log that led to a
        # match failure, so relaxing the config_prompt.
        # Router(config-line)#tion generated from file cdrom1:/ovf-env.xml
        # Added cloud as pattern can be cloud-aws or cloud-azure under redundancy config
        self.config_prompt = r'^(.*)\(.*(con|cfg|ipsec-profile|cloud)\S*\)#\s?$'
