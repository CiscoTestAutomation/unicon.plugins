#!/usr/bin/env python3

import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper
from .mock_device_iosxe import MockDeviceTcpWrapperIOSXE, MockDeviceIOSXE

logger = logging.getLogger(__name__)


class MockDeviceIOSXECat4k(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os="iosxe", **kwargs)

    def cat4k_reload_logs(self, transport, cmd):
        if 'prompt' in self.transport_ports[self.transport_handles[transport]]:
            prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
            if cmd == "" and prompt == "":
                prompt = self.transport_ports[self.transport_handles[transport]]['prompt']
                if len(self.transport_ports) > 1 :
                    self.state_change_switchover(
                        transport, 'cat4k_exec', 'c4k_login')
                    return True

class MockDeviceTcpWrapperIOSXECat4k(MockDeviceTcpWrapper):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='iosxe', **kwargs)

        if 'port' in kwargs:
            kwargs.pop('port')

        self.mockdevice = MockDeviceIOSXECat4k(*args, **kwargs)



def main(args=None):
    logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                        format="%(asctime)s [%(levelname)8s]:  %(message)s")
    if not args:
        parser = argparse.ArgumentParser()
        parser.add_argument('--state', help='initial state')
        parser.add_argument('--ha', action='store_true', help='HA mode')
        parser.add_argument('--hostname', help='Device hostname (default: Switch')
        parser.add_argument('-d', action='store_true', help='Debug')
        args = parser.parse_args()

    if args.d:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    if args.state:
        state = args.state
    else:
        state = 'cat4k_enable,cat4k_locked'
    if args.hostname:
        hostname = args.hostname
    else:
        hostname = 'Switch'

    if args.ha:
        md = MockDeviceTcpWrapperIOSXE(hostname=hostname, state=state)
        md.run()
    else:
        md = MockDeviceIOSXE(hostname=hostname, state=state)
        md.run()


if __name__ == "__main__":
    main()
