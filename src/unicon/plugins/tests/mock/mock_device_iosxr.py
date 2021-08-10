#!/usr/bin/env python3

import re
import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper

logger = logging.getLogger(__name__)

class MockDeviceIOSXR(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='iosxr', **kwargs)

    def enable(self, transport, cmd):
        if re.match('clock set', cmd):
            return True

    def confirm_switchover(self, transport, cmd):
        if cmd == "":
            self.command_handler(transport, cmd)
            if len(self.transport_ports) > 1:
                self.state_change_switchover(transport, 'console_standby', 'switchover_standby')

            return True


class MockDeviceTcpWrapperIOSXR(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='iosxr', **kwargs)
        if 'port' in kwargs:
            kwargs.pop('port')
        self.mockdevice = MockDeviceIOSXR(*args, **kwargs)


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
        state = 'login,console_standby'

    if args.hostname:
        hostname = args.hostname
    else:
        hostname = 'Router'

    if args.ha:
        md = MockDeviceTcpWrapperIOSXR(hostname=hostname, state=state)
        md.run()
    else:
        md = MockDeviceIOSXR(hostname=hostname, state=state)
        md.run()


if __name__ == "__main__":
    main()
