#!/usr/bin/env python3

import re
import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper

logger = logging.getLogger(__name__)

class MockDeviceIOSXE(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os="iosxe", **kwargs)

    def enable_asr(self, transport, cmd):
        if cmd == "redundancy force-switchover":
            if len(self.transport_ports) > 1 :
                self.set_state(self.transport_handles[transport],
                    'asr_exec_standby')
                self.state_change_switchover(
                    transport, 'asr_exec_standby', 'enable_asr')
            return True

    def ha_reload_proceed(self, transport, cmd):
         if 'prompt' in self.transport_ports[self.transport_handles[transport]]:
             prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
             if cmd == "" and prompt == 'Proceed with reload? [confirm]':
                 prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
                 if len(self.transport_ports) > 1 :
                    self.state_change_switchover(
                          transport, 'cat9k_ha_active_console', 'cat9k_ha_standby_console')
                 return True

class MockDeviceTcpWrapperIOSXE(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='iosxe', **kwargs)

        if 'port' in kwargs:
            kwargs.pop('port')

        if 'stack' in kwargs and kwargs['stack']:
            kwargs.pop('stack')
            self.mockdevice = MockDeviceStackIOSXE(*args, **kwargs)
        elif 'quad' in kwargs and kwargs['quad']:
            kwargs.pop('quad')
            self.mockdevice = MockDeviceQuadIOSXE(*args, **kwargs)
        else:
            self.mockdevice = MockDeviceIOSXE(*args, **kwargs)

class MockDeviceStackIOSXE(MockDevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os="iosxe", **kwargs)

    def stack_enable(self, transport, cmd):
        port = self.transport_handles[transport]

        if cmd == 'show switch':
            self.update_show_switch(transport)
        if cmd == "redundancy reload shelf":
            ports = [p for p in self.transport_ports.keys() \
                if p != self.transport_handles[transport]]
            if len(ports):
                for port in ports:
                    self.set_state(port, 'stack_rommon')

    def update_show_switch(self, transport):
        port = self.transport_handles[transport]
        switch_no = self.transport_ports[port]['switch_no']
        data  = 'Switch/Stack Mac Address : 5897.bd36.b380 - Local Mac Address\n'\
                'Mac persistency wait time: Indefinite\n'\
                '                                             H/W   Current\n'\
                'Switch#   Role    Mac Address     Priority Version  State\n'\
                '-------------------------------------------------------------------\n'

        for i in self.transport_ports.values():
            switch_line = '{star}{num}       {role}   5897.bd36.b380     3      V01     {state}  \n'
            if i['switch_no'] == switch_no:
                star = '*'
            else:
                star = ' '
            switch_line = switch_line.format(star=star, num=i['switch_no'], role=i['role'], state=i['switch_state'])
            data += switch_line
        self.mock_data['stack_enable']['commands']['show switch'] = data


class MockDeviceQuadIOSXE(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os="iosxe", **kwargs)

    def quad_enable(self, transport, cmd):
        port = self.transport_handles[transport]
        ports = [p for p in self.transport_ports.keys() if p != port]

        if cmd == "redundancy force-switchover":
            for idx, port in enumerate(ports):
                if idx == 0:
                    # active ics -> standby
                    self.set_state(port, 'quad_stby_switchover')
                elif idx == 1:
                    # standby -> active
                    self.set_state(port, 'quad_enable')
                else:
                    # standby ics -> active ics
                    self.set_state(port, 'quad_ics_login')

        if cmd == "reload":
            for idx, port in enumerate(ports):
                if idx == 1:
                    # standby
                    self.set_state(port, 'quad_stby_reload')
                else:
                    # standby ics / active ics
                    self.set_state(port, 'quad_ics_reload')


def main(args=None):
    logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                        format="%(asctime)s [%(levelname)8s]:  %(message)s")
    if not args:
        parser = argparse.ArgumentParser()
        parser.add_argument('--state', help='initial state')
        parser.add_argument('--ha', action='store_true', help='HA mode')
        parser.add_argument('--hostname', help='Device hostname (default: Router')
        parser.add_argument('-d', action='store_true', help='Debug')
        args = parser.parse_args()

    if args.d:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    if args.state:
        state = args.state
    elif args.ha:
        state = 'asr_exec,asr_exec_standby'
    else:
        state = 'asr_exec'
    if args.hostname:
        hostname = args.hostname
    else:
        hostname = 'Router'

    if args.ha:
        md = MockDeviceTcpWrapperIOSXE(hostname=hostname, state=state)
        md.run()
    else:
        md = MockDeviceIOSXE(hostname=hostname, state=state)
        md.run()


if __name__ == "__main__":
    main()
