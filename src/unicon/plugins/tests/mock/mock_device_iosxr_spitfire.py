#!/usr/bin/env python3

import re
import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper

logger = logging.getLogger(__name__)

class MockDeviceSpitfire(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='iosxr', **kwargs)

    def enable(self, transport, cmd):
        if re.match('clock set', cmd):
            return True

    def spitfire_confirm_switchover(self, transport, cmd):
        if cmd == "":
            self.command_handler(transport, cmd)
            if len(self.transport_ports) > 1:
                self.state_change_switchover(transport, 'spitfire_console_standby', 'spitfire_login')

            return True


class MockDeviceTcpWrapperSpitfire(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='iosxr', **kwargs)
        if 'port' in kwargs:
            kwargs.pop('port')
        self.mockdevice = MockDeviceSpitfire(*args, **kwargs)


def main(args=None):

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
    else:
        if args.ha:
            state = 'spitfire_login,spitfire_console_standby'
        else:
            state = 'spitfire_login'

    if args.hostname:
        hostname = args.hostname
    else:
        hostname = 'Router'

    if args.ha:
        md = MockDeviceTcpWrapperSpitfire(hostname=hostname, state=state)
        md.run()
    else:
        md = MockDeviceSpitfire(hostname=hostname, state=state)
        md.run()


if __name__ == "__main__":
    main()
