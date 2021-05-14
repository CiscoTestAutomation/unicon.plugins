'''
Author: Sam Johnson
Contact: samuel.johnson@gmail.com
https://github.com/TestingBytes

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.plugins.generic.service_implementation import Execute as GenericExecute
from unicon.plugins.generic.service_implementation import Switchto as GenericSwitchto
from unicon.plugins.generic.service_implementation import Traceroute as GenericTraceroute


class GaiaExecute(GenericExecute):
    pass


class GaiaTraceroute(GenericTraceroute):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.start_state = 'clish'
        self.end_state = 'clish'

    def call_service(self, addr, command='traceroute', timeout=None, error_pattern=None, **kwargs):
        super().call_service(
            addr,
            command=f'traceroute {addr}',
            timeout=timeout,
            error_pattern=error_pattern,
            **kwargs)


class GaiaSwitchTo(GenericSwitchto):
    pass
