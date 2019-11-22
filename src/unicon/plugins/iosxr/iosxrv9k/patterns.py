__author__ = "Syed Raza <syedraza@cisco.com>"

from ..patterns import IOSXRPatterns

# This module contains all the patterns required in the IOSXRV9K implementation.

class IOSXRV9KPatterns(IOSXRPatterns):
    def __init__(self):
        super().__init__()
        self.xr_launch_final_message = r'^.*:\w+\.\d+\s:\s\w+\[\d+\]:\s+\%.*vm_manager started VM\s\w+.*'
