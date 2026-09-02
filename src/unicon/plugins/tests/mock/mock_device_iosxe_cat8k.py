#!/usr/bin/env python3

import re
import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper
from .mock_device_iosxe import MockDeviceTcpWrapperIOSXE, MockDeviceIOSXE

logger = logging.getLogger(__name__)


class MockDeviceIOSXECat8k(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os="iosxe", **kwargs)


class MockDeviceTcpWrapperIOSXECat8k(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='iosxe', **kwargs)

        if 'port' in kwargs:
            kwargs.pop('port')

        self.mockdevice = MockDeviceIOSXECat8k(*args, **kwargs)


def main(args=None):
    logging.basicConfig(stream=sys.stderr, level=logging.INFO,
                        format="%(asctime)s [%(levelname)8s]:  %(message)s")
    if not args:
        parser = argparse.ArgumentParser()
        parser.add_argument('--state', help='initial state')
        parser.add_argument('--hostname', help='Device hostname (default: Switch')
        parser.add_argument('-d', action='store_true', help='Debug')
        args = parser.parse_args()

    if args.d:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    if args.state:
        state = args.state
    else:
        state = 'cat8k_enable'

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
