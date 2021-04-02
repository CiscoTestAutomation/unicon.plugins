'''
Author: Sam Johnson
Contact: samuel.johnson@gmail.com
https://github.com/TestingBytes

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''
from unicon.core.errors import SubCommandFailure
from unicon.bases.routers.services import BaseService, Statement

from unicon.plugins.generic.service_implementation import Execute as GenericExecute

class GaiaExecute(GenericExecute):
    pass

class GaiaTraceroute(BaseService):

    def __init__(self, connection, context, **kwargs):
        self.connection = connection
        self.context = context
        self.timeout_pattern = ['Timeout occurred', ]
        self.error_pattern = [r'Cannot handle \"host\" cmdline arg',
                                r'connect: Invalid argument',
                                r'Bad option']
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.result = None
        self.timeout = 60*20

        # add the keyword arguments to the object
        self.__dict__.update(kwargs)

    def call_service(self, addr, **kwargs):
        con = self.connection
        cmd = 'traceroute ' + addr
        con.spawn.sendline(cmd)

        try:
            # Wait for prompt
            state = con.state_machine.get_state('enable')
            self.result = con.spawn.expect(state.pattern, self.timeout).match_output
        except Exception:
            raise SubCommandFailure('traceroute failed')

        if self.result.rfind(self.connection.hostname):
            self.result = self.result[:self.result.rfind(self.connection.hostname)].strip()            