#!/usr/bin/env python3

'''
Author: Richard Day
Contact: https://www.linkedin.com/in/richardday/, https://github.com/rich-day

Contents largely inspired by sample Unicon repo:
https://github.com/CiscoDevNet/pyats-plugin-examples/tree/master/unicon_plugin_example/src/unicon_plugin_example
'''

import re
import sys
import logging
import argparse

from unicon.mock.mock_device import MockDevice, MockDeviceTcpWrapper

logger = logging.getLogger(__name__)


class MockDeviceEOS(MockDevice):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='eos', **kwargs)


class MockDeviceTcpWrapperEOS(MockDeviceTcpWrapper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, device_os='eos', **kwargs)
        self.mockdevice = MockDeviceEOS(*args, **kwargs)


def main(args=None):

    if not args:
        parser = argparse.ArgumentParser()
        parser.add_argument('--state', help='initial state')
        parser.add_argument('--hostname', help='Device hostname (default: Switch')
        parser.add_argument('-d', action='store_true', help='Debug')
        args = parser.parse_args()

    if args.d:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    state = args.state or 'exec'
    hostname = args.hostname or 'Switch'
    md = MockDeviceEOS(hostname=hostname, state=state)
    md.run()


if __name__ == "__main__":
    main()
