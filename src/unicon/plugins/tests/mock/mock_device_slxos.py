#!/usr/bin/env python3

'''
Author: Fabio Pessoa Nunes
Contact: https://www.linkedin.com/in/fpessoanunes/

'''

import re
import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper

logger = logging.getLogger(__name__)


class MockDeviceSlxos(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='slxos', **kwargs)


class MockDeviceTcpWrapperSlxos(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='slxos', **kwargs)
        self.mockdevice = MockDeviceSlxos(*args, **kwargs)


def main(args=None):

    if not args:
        parser = argparse.ArgumentParser()
        parser.add_argument('--state', help='initial state')
        parser.add_argument('--hostname', help='Device hostname (default: SLX')
        parser.add_argument('-d', action='store_true', help='Debug')
        args = parser.parse_args()

    if args.d:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    state = args.state or 'user_access_veri'
    hostname = args.hostname or 'SLX'
    md = MockDeviceSlxos(hostname=hostname, state=state)
    md.run()


if __name__ == "__main__":
    main()
