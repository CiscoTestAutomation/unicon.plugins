#!/usr/bin/env python3

import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper

logger = logging.getLogger(__name__)

class MockDeviceDnos6(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='dnos6', **kwargs)


class MockDeviceTcpWrapperDnos6(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='dnos6', **kwargs)
        self.mockdevice = MockDeviceDnos6(*args, **kwargs)


def main(args=None):

    if not args:
        parser = argparse.ArgumentParser()
        parser.add_argument('--state', help='initial state')
        parser.add_argument('--hostname', help='Device hostname (default: Router')
        parser.add_argument('-d', action='store_true', help='Debug')
        args = parser.parse_args()

    if args.d:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    state = args.state or 'login,console_standby'
    hostname = args.hostname or 'DellOS6'
    md = MockDeviceDnos6(hostname=hostname, state=state)
    md.run()


if __name__ == "__main__":
    main()
