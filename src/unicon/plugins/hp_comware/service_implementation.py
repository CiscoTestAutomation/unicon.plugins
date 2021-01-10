'''
Author: Renato Almeida de Oliveira
Contact: renato.almeida.oliveira@gmail.com
https://twitter.com/ORenato_Almeida
https://www.youtube.com/c/RenatoAlmeidadeOliveira
Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

from unicon.bases.routers.services import BaseService
from unicon.core.errors import SubCommandFailure
from unicon.eal.dialogs import Dialog
from unicon.plugins.generic.service_implementation import Execute as GenericExecute
from unicon.plugins.hp_comware.service_statements import (
 save_confirm,
 file_path,
 save_overwrite)



class HPExecute(GenericExecute):

    def __init__(self, connection, context, **kwargs):
        super().__init__(connection, context, **kwargs)
        self.dialog += Dialog([save_confirm, 
                               file_path,
                               save_overwrite])


class HPComwarePing(BaseService):

    def __init__(self, connection, context, **kwargs):
        self.connection = connection
        self.context = context
        self.timeout_pattern = ['Timeout occurred', ]
        self.error_pattern = [r'Unknown host', r'Incorrect', r'HELP']
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.result = None
        self.timeout = 60

        # add the keyword arguments to the object
        self.__dict__.update(kwargs)

    def call_service(self, addr, proto='ip', **kwargs):
        con = self.connection
        timeout = self.timeout
        cmd = 'ping '
        if((proto == 'ip') or (proto == 'ipv6')):
            cmd = cmd + proto + " "
        else:
            raise SubCommandFailure("Protocol should be ip or ipv6")
        if('src_addr' in kwargs):
            src_addr = kwargs['src_addr']
            source_cmd = f"-a {src_addr} "
            cmd = cmd + source_cmd
        if('count' in kwargs):
            count = kwargs['count']
            count_cmd = f"-c {count} "
            cmd = cmd + count_cmd
        if('vrf' in kwargs):
            vrf = kwargs['vrf']
            vrf_cmd = f"-vpn-instance {vrf} "
            cmd = cmd + vrf_cmd
        if('ttl' in kwargs):
            ttl = kwargs['ttl']
            ttl_cmd = f"-h {ttl} "
            cmd = cmd + ttl_cmd

        cmd = cmd + addr
        con.spawn.sendline(cmd)

        # It seems we also want to return the command sent
        # con.spawn.expect([cmd])

        try:
            # Wait for prompt
            state = con.state_machine.get_state('enable')
            self.result = con.spawn.expect(state.pattern, timeout=timeout).match_output
        except Exception:
            raise SubCommandFailure('Ping failed')

        if self.result.rfind(self.connection.hostname):
            self.result = self.result[:self.result.rfind(self.connection.hostname)].strip()


class HPComwareTraceroute(BaseService):

    def __init__(self, connection, context, **kwargs):
        self.connection = connection
        self.context = context
        self.timeout_pattern = ['Timeout occurred', ]
        self.error_pattern = [r'Destination not found inside Max Hop Count',
                              r'Incorrect', r'HELP']
        self.start_state = 'enable'
        self.end_state = 'enable'
        self.result = None
        self.timeout = 60*20

        # add the keyword arguments to the object
        self.__dict__.update(kwargs)

    def call_service(self, addr, proto='ip', **kwargs):
        con = self.connection
        timeout = self.timeout
        cmd = 'tracert '
        if((proto == 'ip') or (proto == 'ipv6')):
            if(proto == 'ipv6'):
                cmd = cmd + proto + " "
        else:
            raise SubCommandFailure("Protocol should be ip or ipv6")
        if('src_addr' in kwargs):
            src_addr = kwargs['src_addr']
            source_cmd = f"-a {src_addr} "
            cmd = cmd + source_cmd
        if('count' in kwargs):
            count = kwargs['count']
            count_cmd = f"-q {count} "
            cmd = cmd + count_cmd
        if('vrf' in kwargs):
            vrf = kwargs['vrf']
            vrf_cmd = f"-vpn-instance {vrf} "
            cmd = cmd + vrf_cmd
        if('min_ttl' in kwargs):
            min_ttl = kwargs['min_ttl']
            min_ttl_cmd = f"-f {min_ttl} "
            cmd = cmd + min_ttl_cmd
        if('max_ttl' in kwargs):
            max_ttl = kwargs['max_ttl']
            max_ttl_cmd = f"-m {max_ttl} "
            cmd = cmd + max_ttl_cmd

        cmd = cmd + addr
        con.spawn.sendline(cmd)

        # It seems we also want to return the command sent
        # con.spawn.expect([cmd])

        try:
            # Wait for prompt
            state = con.state_machine.get_state('enable')
            self.result = con.spawn.expect(state.pattern, timeout=timeout).match_output
        except Exception:
            raise SubCommandFailure('Traceroute failed')

        if self.result.rfind(self.connection.hostname):
            self.result = self.result[:self.result.rfind(self.connection.hostname)].strip()

