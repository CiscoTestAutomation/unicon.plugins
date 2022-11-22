#!/usr/bin/env python3

import re
import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper

logger = logging.getLogger(__name__)

class MockDeviceJunos(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='junos', **kwargs)


class MockDeviceTcpWrapperJunos(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='junos', **kwargs)
        self.mockdevice = MockDeviceJunos(*args, **kwargs)


def main(args=None):

    if not args:
        parser = argparse.ArgumentParser()
        parser.add_argument('--state', help='initial state')
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

    md = MockDeviceJunos(hostname=hostname, state=state)
    md.run()


if __name__ == "__main__":
    main()
