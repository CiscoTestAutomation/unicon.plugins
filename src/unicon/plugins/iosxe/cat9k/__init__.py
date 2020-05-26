""" cat9k IOS-XE connection implementation.
"""

__author__ = "Rob Trotter <rlt@cisco.com>"


from unicon.plugins.iosxe import IosXESingleRpConnection, IosXEDualRPConnection  

class IosXECat9kSingleRpConnection(IosXESingleRpConnection):
    series = 'cat9k' 


class IosXECat9kDualRPConnection(IosXEDualRPConnection):
    series = 'cat9k'
