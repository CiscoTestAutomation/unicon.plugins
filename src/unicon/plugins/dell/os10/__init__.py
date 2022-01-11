'''
Author: Knox Hutchinson
Contact: https://dataknox.dev
https://twitter.com/data_knox
https://youtube.com/c/dataknox
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.plugins.dell import DellSingleRPConnection

class Dellos10SingleRPConnection(DellSingleRPConnection):
    '''DellosSingleRPConnection

    Dell OS10 platform support
    '''
    platform = 'os10'
